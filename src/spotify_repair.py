import time, csv, requests

from src.utils import has_unwanted_keywords, is_unwanted, join_artists, get_token, rate_limited_get, load_json, save_json
from src.musicbrain import localize_artist
from src.utils import SPOTIFY_CACHE_FILE, FIXED_ID_FILE

_spotify_cache  = load_json(SPOTIFY_CACHE_FILE)
_fixed_ids:set  = set(load_json(FIXED_ID_FILE) or [])

def spotify_search(song: str, artist: str, album: str) -> dict | None:
    cache_key = f"{song}|||{artist}|||{album}"
    filter_enabled = not has_unwanted_keywords(song) and not has_unwanted_keywords(album)

    queries = [
        f'track:"{song}" album:"{album}"' if album else f'track:"{song}"',
        f'track:"{song}"',
    ]
    
    matched_item = None
    for query in queries:
        try:
            resp = rate_limited_get(
                "https://api.spotify.com/v1/search",
                headers={"Authorization": f"Bearer {get_token()}"},
                params={"q": query, "type": "track", "limit": 5},
                timeout=10,
            )
            if resp.status_code == 429:
                wait = min(int(resp.headers.get("Retry-After", 5)), 30)
                print(f"    ⏳ 429, Wait {wait}s...")
                time.sleep(wait + 1)
                continue

            resp.raise_for_status()
            items = resp.json().get("tracks", {}).get("items", [])
            time.sleep(1)

            if not items:
                continue

            if filter_enabled:
                clean_items = [i for i in items if not is_unwanted(i)]
                if not clean_items:
                    clean_items = items
            else:
                clean_items = items

            matched_item = next(
                (i for i in clean_items if i["name"].lower() == song.lower()),
                clean_items[0]
            )
            break

        except Exception as e:
            print(f"    ⚠️  error: {e}")
            time.sleep(2)

        if matched_item:
            break 

    if not matched_item:
        return None

    track_artists = [localize_artist(a["name"]) for a in matched_item["artists"]]
    album_artists = [localize_artist(a["name"]) for a in matched_item["album"]["artists"]]

    result = {
        "name":              matched_item["name"],
        "artist":            join_artists(track_artists),
        "album_artist":      join_artists(album_artists),
        "album":             matched_item["album"]["name"],
        "sort_name":         matched_item["name"],
        "sort_artist":       join_artists(track_artists),
        "sort_album_artist": join_artists(album_artists),
        "sort_album":        matched_item["album"]["name"],
    }

    return result

def spotify_main():
    with open("data/music_library.csv", encoding="utf-8") as f:
        tracks = list(csv.DictReader(f))

    print(f"📚 In total {len(tracks)} songs, starting...\n")

    for i, t in enumerate(tracks):
        song   = t["name"].strip()
        artist = t["artist"].strip()
        album  = t["album"].strip()
        db_id = t["db_id"].strip()

        if db_id in _fixed_ids:
            continue

        cache_key = f"{song}|||{artist}|||{album}"
        if cache_key in _spotify_cache:
            continue

        print(f"[{i+1}/{len(tracks)}] {song} — {artist}")
        spotify = spotify_search(song, artist, album)
        row = dict(t)
        if spotify:
            row["name"]         = spotify.get("name", song)
            row["artist"]       = spotify.get("artist", artist)
            row["album_artist"] = spotify.get("album_artist", artist)
            row["album"]        = spotify.get("album", album)   
            row["sort_name"]         = spotify.get("name", song)
            row["sort_artist"]       = spotify.get("artist", artist)
            row["sort_album_artist"] = spotify.get("album_artist", artist)
            row["sort_album"]        = spotify.get("album", album)  

            _spotify_cache[cache_key] = row
            save_json(SPOTIFY_CACHE_FILE, _spotify_cache) 
        if not spotify:
            print(f"  {song} ❌ Not found, keeping original value")
            _spotify_cache[cache_key] = None
            save_json(SPOTIFY_CACHE_FILE, _spotify_cache)

    print(f"\n✅ Done!")

if __name__ == "__main__":
    resp = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {get_token()}"},
        params={"q": 'track:"Complicated"', "type": "track", "limit": 1},
        timeout=10,
    )
    print(resp.status_code)
    print(f"    ⚠️  HTTP {resp.status_code}: {resp.text}")

    if resp.status_code == 200:
        spotify_main()