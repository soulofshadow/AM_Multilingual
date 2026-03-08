# ── MusicBrainz ───────────────────────────────────────
import requests, time

from src.utils import AREA_TO_LOCALE, MB_HEADERS, _s2t, _t2s, save_json, load_json
from src.utils import ARTIST_CACHE_FILE, MB_CACHE_FILE

_artist_cache   = load_json(ARTIST_CACHE_FILE)   # spotify_id → localized name
_mb_cache       = load_json(MB_CACHE_FILE)        # spotify_name → {area, mbid, aliases}

def mb_get(path, params):
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://musicbrainz.org/ws/2/{path}",
                params={**params, "fmt": "json"},
                headers=MB_HEADERS, timeout=15,
            )
            resp.raise_for_status()
            time.sleep(1.1)
            return resp.json()
        except Exception as e:
            wait = (attempt + 1) * 3
            print(f"    ⚠️  MB error (attempt {attempt+1}/3), wait {wait}s: {e}")
            time.sleep(wait)
    return None

def find_in_cache_by_alias(name: str) -> dict | None:
    for cached_name, info in _mb_cache.items():
        if info is None:
            continue
        aliases = info.get("aliases", {})
        if name in aliases.values():
            return info
    return None

def get_mb_info(spotify_name: str) -> dict:
    """Check MusicBrainz: return area + aliases"""
    if spotify_name in _mb_cache:
        return _mb_cache[spotify_name]
    
    found = find_in_cache_by_alias(spotify_name)
    if found:
        _mb_cache[spotify_name] = found
        save_json(MB_CACHE_FILE, _mb_cache)
        return found
    
    # Step 1: Search artist by Spotify name to get MBID and area
    data = mb_get("artist", {"query": f'{spotify_name}', "limit": 1})
    if not data or not data.get("artists"):
        result = {"area": None, "aliases": {}}
        _mb_cache[spotify_name] = result
        save_json(MB_CACHE_FILE, _mb_cache)
        return result

    artist  = data["artists"][0]
    area    = artist.get("area", {}).get("name")
    mbid    = artist["id"]

    # Step 2: Search artist detail by MBID to get aliases
    detail  = mb_get(f"artist/{mbid}", {"inc": "aliases"})
    aliases = {}
    if detail:
        for a in detail.get("aliases", []):
            locale = a.get("locale")
            if not locale:
                continue
            # primary alias takes precedence if multiple aliases share the same locale
            if locale not in aliases or a.get("primary") == "primary":
                aliases[locale] = a["name"]

    if area in ["China", "Taiwan", "Hong Kong", "Singapore", "Malaysia"]:
        # For Chinese artists, also add a fallback alias without locale to handle cases where locale is missing or incorrect in MB
        zh_value = None
        for key, val in aliases.items():
            if "zh" in key.lower():
                zh_value = val
                break
        if zh_value:
            if "zh_Hans" not in aliases:
                aliases["zh_Hans"] = _t2s.convert(zh_value)
            if "zh_Hant" not in aliases:
                aliases["zh_Hant"] = _s2t.convert(zh_value)

    result = {"area": area, "aliases": aliases}
    _mb_cache[spotify_name] = result
    save_json(MB_CACHE_FILE, _mb_cache)
    return result

def localize_artist(spotify_name: str) -> str:
    if spotify_name in _artist_cache:
        return _artist_cache[spotify_name]

    mb    = get_mb_info(spotify_name)
    area  = mb["area"]
    locale = AREA_TO_LOCALE.get(area)

    if not locale:
        result = spotify_name
    else:
        result = mb["aliases"].get(locale, spotify_name)

    _artist_cache[spotify_name] = result
    save_json(ARTIST_CACHE_FILE, _artist_cache)
    return result