import json, csv
from tqdm import tqdm

from google import genai
from google.genai import types
from .utils import GEMINI_API, MODEL_NAME, MODEL_CAPS, QUERY_TEMPLATE, METADATA_SCHEMA
from .utils import rate_limited_call

from .musicbrain import localize_artist, get_artist_locale

from .utils import MUSIC_LIBRARY_FILE, RECORDING_CACHE_FILE, FIXED_CACHE_FILE, FAILED_LOG_FILE
from .utils import load_json, save_json, split_artists, join_artists
from .utils import to_sort_string


def build_generation_config(model_name: str) -> types.GenerateContentConfig:
    caps = MODEL_CAPS.get(model_name, {"google_search": False, "json_schema": False})
    kwargs = {}
    if caps["json_schema"]:
        kwargs["response_mime_type"] = "application/json"
        kwargs["response_json_schema"] = METADATA_SCHEMA
    if caps["google_search"]:
        kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    return types.GenerateContentConfig(**kwargs)

def _gemini_generate(client, config, prompt):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config
    )

def llm_correct_metadata(client, config, song: str, artist: str, album: str) -> dict | None:
    prompt = QUERY_TEMPLATE.format(song=song, artist=artist, album=album)

    try:
        resp = rate_limited_call(_gemini_generate, client, config, prompt)
        if not resp.text:
            return None
        text = resp.text.strip()
        start = text.find("{")
        end   = text.rfind("}") + 1
        data = json.loads(text[start:end])

        if not isinstance(data, dict):
            return None
        return data
    except Exception as e:
        return None

def patch_sort_fields(corrected: dict):
    locale = get_artist_locale(split_artists(corrected.get("artist_name", ""))[0])

    if locale:
        # CJK
        corrected["sort_name"]         = to_sort_string(corrected["song_name"], locale)
        corrected["sort_artist"]       = to_sort_string(corrected["artist_name"], locale)
        corrected["sort_album_artist"] = to_sort_string(corrected["album_artist_name"], locale)
        corrected["sort_album"]        = to_sort_string(corrected["album_name"], locale)
    else:
        # Latin
        corrected["sort_name"]         = corrected["song_name"]
        corrected["sort_artist"]       = corrected["artist_name"]
        corrected["sort_album_artist"] = corrected["album_artist_name"]
        corrected["sort_album"]        = corrected["album_name"]
        
    return corrected

def patch_metadata(client, config, song: str, artist: str, album: str) -> dict | None:

    corrected = llm_correct_metadata(client, config, song, artist, album)
    if not corrected:
        return None
    
    track_artists = [localize_artist(a) for a in split_artists(corrected.get("artist_name", artist))]
    album_artists = [localize_artist(a) for a in split_artists(corrected.get("album_artist_name", artist))]
    corrected["artist_name"] = join_artists(track_artists)
    corrected["album_artist_name"] = join_artists(album_artists)

    corrected = patch_sort_fields(corrected)
    return corrected

def gemini_main(recording_cache, fixed_cache, client, config):
    with open(MUSIC_LIBRARY_FILE, encoding="utf-8") as f:
        tracks = list(csv.DictReader(f))

    count = 0
    needs_review = []
    pbar = tqdm(enumerate(tracks), total=len(tracks), desc="    Processing", ncols=100)
    for _, t in pbar:
        pbar.set_postfix_str(f"{t['name'][:20]:<20} — {t['artist'][:15]:<15}")

        db_id = t["db_id"].strip()
        if db_id in fixed_cache or db_id in recording_cache:
            continue

        # Start processing
        song   = t["name"].strip()
        artist = t["artist"].strip()
        album  = t["album"].strip()
        gemini_result = patch_metadata(client, config, song, artist, album)
        if gemini_result:
            t.update(gemini_result)
            recording_cache[db_id] = t
            save_json(RECORDING_CACHE_FILE, recording_cache)

            # log failed reviews for manual checking
            if gemini_result.get("needs_review"):
                needs_review.append({
                    "db_id": db_id,
                    "type": "OLD",
                    "name": t["name"], 
                    "artist": t["artist"],
                    "album_artist": t["album_artist"],
                    "album": t["album"],
                    "confirmed": ""
                })
                needs_review.append({
                    "db_id": "",
                    "type": "NEW",
                    "name": gemini_result.get("song_name"),
                    "artist": gemini_result.get("artist_name"),
                    "album_artist": gemini_result.get("album_artist_name"),
                    "album": gemini_result.get("album_name"),
                    "confirmed": 0
                })
        count += 1

        
    print(f"    Done! Processed {count} tracks, {len(needs_review)} need review.")
    return needs_review


if __name__ == "__main__":

    recording_cache  = load_json(RECORDING_CACHE_FILE)
    fixed_cache:set  = set(load_json(FIXED_CACHE_FILE) or [])

    client = genai.Client(api_key=GEMINI_API)
    config = build_generation_config(MODEL_NAME)

    # Check API connectivity and model availability before the main loop to avoid wasting time on multiple failed attempts.
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents='Reply with this exact JSON only: {"status": "ok"}'
    )
    resp = json.loads(resp.text)

    if resp['status'] == 'ok':
        print(f"🤖  Gemini API is working and model {MODEL_NAME} is ready...")
        needs_review = gemini_main(recording_cache, fixed_cache, client, config)
        if needs_review:
            with open(FAILED_LOG_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=needs_review[0].keys())
                writer.writeheader()
                writer.writerows(needs_review)
        print(f"🤖  Gemini work completed successfully!")