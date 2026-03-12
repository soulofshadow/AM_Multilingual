import csv
from .utils import FAILED_LOG_FILE, RECORDING_CACHE_FILE
from .utils import load_json, save_json
from .utils import to_sort_string, split_artists
from .musicbrain import get_artist_locale

def patch_sort_fields(corrected: dict):
    locale = get_artist_locale(split_artists(corrected.get("artist_name", ""))[0])
    if not locale:
        return corrected
    corrected["sort_name"]         = to_sort_string(corrected["song_name"], locale)
    corrected["sort_artist"]       = to_sort_string(corrected["artist_name"], locale)
    corrected["sort_album_artist"] = to_sort_string(corrected["album_artist_name"], locale)
    corrected["sort_album"]        = to_sort_string(corrected["album_name"], locale)
    return corrected

def manual_repair(cache: dict, rows: list[dict]):
    skipped = 0
    updated = 0
    for row in rows:
        if row.get("confirmed", "0") != "1":
            skipped += 1
            continue  

        name   = row["name"].strip()
        artist = row["artist"].strip()
        album_artist = row["album_artist"].strip()
        album  = row["album"].strip()
        key    = f"{name}|||{artist}|||{album}"

        if key not in cache:
            print(f"    Key not found in cache, skipping: {key}")
            skipped += 1
            continue

        entry = cache[key]

        corrected_name   = row.get("corrected_name", "").strip()
        corrected_artist = row.get("corrected_artist", "").strip()
        corrected_album_artist = row.get("corrected_album_artist", "").strip()
        corrected_album  = row.get("corrected_album", "").strip()
        

        if corrected_name:
            entry["song_name"] = corrected_name
        if corrected_artist:
            entry["artist_name"] = corrected_artist
        if corrected_album:
            entry["album_name"] = corrected_album
        if corrected_album_artist:
            entry["album_artist_name"] = corrected_album_artist

        entry = patch_sort_fields(entry)
        entry["needs_review"]   = False
        entry["review_reason"]  = "manually_verified"

        cache[key] = entry
        updated += 1
        print(f"    Updated: {name} — {artist}")

    save_json(RECORDING_CACHE_FILE, cache)
    print(f"    Done. {updated} updated, {skipped} skipped.")
    
    remaining = [r for r in rows if r.get("confirmed", "0") != "1"]
    if len(remaining) < len(rows):
        with open(FAILED_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(remaining)
        print(f"    Removed {len(rows) - len(remaining)} confirmed rows from {FAILED_LOG_FILE}")

if __name__ == "__main__":

    recording_cache  = load_json(RECORDING_CACHE_FILE)

    print("💁‍♂️ Reading manual review log...")
    with open(FAILED_LOG_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"    Found {len(rows)} entries to update")
    manual_repair(recording_cache, rows)
    print("💁‍♂️ Manual repair completed!")