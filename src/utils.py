import os
from dotenv import load_dotenv
import re, time, json

import opencc
from pypinyin import lazy_pinyin, Style
import pykakasi
import hangul_romanize
from hangul_romanize.rule import academic

load_dotenv() 

# -----------------------------------------------------
# -----------------------------------------------------
# Gemini API key
GEMINI_API    = os.environ["GEMINI_API_KEY"]
MODEL_NAME = "gemini-3.1-flash-lite-preview"
PAID_USER = os.environ.get("PAID_USER", "false").lower() == "true"
# Cache files
RECORDING_CACHE_FILE = "cache/recording_cache.json"
ARTIST_CACHE_FILE  = "cache/artist_cache.json"
MB_CACHE_FILE      = "cache/mb_cache.json"
FIXED_CACHE_FILE   = "cache/fixed_cache.json"
# Music library file
MUSIC_LIBRARY_FILE = "data/music_library.csv"
FAILED_LOG_FILE    = "data/needs_review.csv"

os.makedirs("cache", exist_ok=True)
os.makedirs("data", exist_ok=True)
# -----------------------------------------------------
# -----------------------------------------------------

# Global variables
MB_HEADERS = {"User-Agent": "MusicLibraryFixer/1.0 (soulofshadow@foxmail.com)"}

FIELDS = ["db_id", "name", "artist", "album_artist", "album",
          "sort_name", "sort_artist", "sort_album_artist", "sort_album"]

AREA_TO_LOCALE = {
    "China":        "zh_Hans",
    "Taiwan":       "zh_Hant",
    "Hong Kong":    "zh_Hant",
    "Singapore":    "zh_Hans",
    "Malaysia":     "zh_Hans",
    "Japan":        "ja",
    "South Korea":  "ko",
}

MODEL_CAPS = {
    "gemini-3.1-flash-lite-preview": {
        "google_search": True if PAID_USER else False,  # Google Search tool is only available for paid-tier API keys
        "json_schema":   True,
        "response_time": 0.5 if PAID_USER else 6,  # Paid-tier keys generally get faster responses, but this can vary
    }
}

QUERY_TEMPLATE = """
I have a song with possibly incorrect or transliterated metadata.

Input:
- Song: {song}
- Artist: {artist}
- Album: {album}

Tasks:
1. Find the most likely correct metadata.
2. Use Google Search when needed, especially for newer songs or uncertain cases.
3. Return metadata in the original language/script.
4. Identify the original release country.
5. Return only JSON matching the schema.

Rules:
- return these fields: song_name, artist_name, album_artist_name, album_name, country, language, needs_review.
- song_name and album_name should be in the original language/script.
- artist_name must contain ALL track artists. (ALL artists separated by ", " and "&" for the last one, e.g. "A, B & C". Do NOT use "feat.", "ft.", "with" or any other prefix. Just list all artist names.)
- album_artist_name should be the main album artist.
- country should be the original release country, such as China, Japan, Hong Kong, Taiwan, USA.
- language should indicate the primary language/script of the original metadata, such as Traditional Chinese, Japanese, Simplified Chinese, English.
- Set needs_review=true if:
  - the song may be a newer release and sources are limited,
  - search results conflict,
  - album title is uncertain,
  - artist identity is ambiguous,
  - you are not confident enough to safely overwrite the user's original metadata.
- If needs_review=true, still return your best guess.
- Only return JSON, no explanations or extra text.
"""

METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "song_name": {
            "type": "string",
            "description": "Correct track title in the original language."
        },
        "artist_name": {
            "type": "string",
            "description": 'All track artists formatted exactly as "A, B & C", without feat., ft., featuring, or with.'
        },
        "album_artist_name": {
            "type": "string",
            "description": "Main album artist, usually the primary artist."
        },
        "album_name": {
            "type": "string",
            "description": "Correct album name in the original language."
        },
        "country": {
            "type": "string",
            "description": "Original release country, such as China, Japan, Hong Kong, Taiwan, USA."
        },
        "language": {
            "type": "string",
            "description": "Primary language/script of the original metadata, such as Traditional Chinese, Japanese, Simplified Chinese, English."
        },
        "needs_review": {
            "type": "boolean",
            "description": "True if the result is uncertain, conflicting, ambiguous, or not reliable enough to overwrite the original metadata automatically."
        }
    },
    "required": [
        "song_name",
        "artist_name",
        "album_artist_name",
        "album_name",
        "country",
        "language",
        "needs_review"
    ],
    "additionalProperties": False
}

REQUEST_INTERVAL = MODEL_CAPS.get(MODEL_NAME, {}).get("response_time", 1.1) + 0.1 # add buffer
_last_request_time = 0
_s2t = opencc.OpenCC('s2t')
_t2s = opencc.OpenCC('t2s')
_kks = pykakasi.kakasi()
_hangul = hangul_romanize.Transliter(academic)


# File read/write utilities
def load_json(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}

def save_json(path, data):
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# API rate limiting
def rate_limited_call(func, *args, **kwargs):
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    result = func(*args, **kwargs)
    _last_request_time = time.time()
    return result

# Artist name localization
def join_artists(parts: list[str]) -> str:
    """['A', 'B', 'C'] → 'A, B & C'"""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " & " + parts[-1]

def split_artists(artist_str: str) -> list[str]:
    """'A, B & C' → ['A', 'B', 'C']"""
    parts = re.split(r"\s*&\s*|\s*,\s*", artist_str)
    return [p.strip() for p in parts if p.strip()]

def to_sort_string(text: str, locale: str) -> str:
    if locale in ("zh_Hans", "zh_Hant"):
        pinyin = lazy_pinyin(text, style=Style.NORMAL)
        return " ".join(p.capitalize() for p in pinyin)
    elif locale == "ja":
        result = _kks.convert(text)
        return " ".join(item["hepburn"].capitalize() for item in result if item["hepburn"])
    elif locale == "ko":
        return _hangul.translit(text)
    else:
        return text

