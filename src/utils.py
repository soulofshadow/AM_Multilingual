import re, time, base64, requests, opencc, json, os
from dotenv import load_dotenv
import os


load_dotenv() 
# -----------------------------------------------------
# -----------------------------------------------------
# SPotify API credentials (for client credentials flow)
CLIENT_ID     = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
# Gemini API key
GEMINI_API    = os.environ["GEMINI_API_KEY"]
# Cache and data files
SPOTIFY_CACHE_FILE = "data/spotify_cache.json"
ARTIST_CACHE_FILE  = "data/artist_cache.json"
MB_CACHE_FILE      = "data/mb_cache.json"
FIXED_ID_FILE      = "data/fixed_ids.json"
# -----------------------------------------------------
# -----------------------------------------------------


REQUEST_INTERVAL = 1.0
_last_request_time = 0

MB_HEADERS    = {"User-Agent": "MusicLibraryFixer/1.0 (soulofshadow@foxmail.com)"}

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

UNWANTED_KEYWORDS = [
    "karaoke", "instrumental", "remix", "cover", "tribute",
    "originally performed", "made famous", "backing track",
    "re-record", "rerecord", "acoustic version", "live version", 
    "radio edit", "workout mix", "workout remix", "version", "edit"
]

_token       = None
_token_expiry = 0

_s2t = opencc.OpenCC('s2t')
_t2s = opencc.OpenCC('t2s')

#
def rate_limited_get(url, **kwargs):
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    resp = requests.get(url, **kwargs)
    _last_request_time = time.time()
    return resp

def get_token() -> str:
    global _token, _token_expiry
    if _token and time.time() < _token_expiry - 60:
        return _token
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {creds}"},
        data={"grant_type": "client_credentials"},
    )
    resp.raise_for_status()
    _token = resp.json()["access_token"]
    _token_expiry = time.time() + 3600
    return _token

def load_json(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}

def save_json(path, data):
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def join_artists(parts: list[str]) -> str:
    """['A', 'B', 'C'] → 'A, B & C'"""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " & " + parts[-1]

def split_artists(artist_str: str) -> list[str]:
    """'A, B & C' → ['A', 'B', 'C']"""
    parts = re.split(r"\s*&\s*|\s*,\s*", artist_str)
    return [p.strip() for p in parts if p.strip()]


def has_unwanted_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in UNWANTED_KEYWORDS)

def is_unwanted(item: dict) -> bool:
    name        = item["name"].lower()
    album_name  = item["album"]["name"].lower()

    for kw in UNWANTED_KEYWORDS:
        if kw in name or kw in album_name:
            return True
    return False