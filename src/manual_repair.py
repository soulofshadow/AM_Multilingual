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

    for old_row, new_row in zip(rows[0::2], rows[1::2]):
        if new_row.get("confirmed", "0") != "1":
            skipped += 1
            continue

        db_id = old_row["db_id"]
        if db_id not in cache:
            print(f"    Key not found in cache, skipping: {db_id}")
            skipped += 1
            continue

        entry = cache[db_id]
        entry["song_name"] = new_row["name"]
        entry["artist_name"] = new_row["artist"]
        entry["album_artist_name"] = new_row["album_artist"]
        entry["album_name"] = new_row["album"]

        entry = patch_sort_fields(entry)
        entry["needs_review"]   = False
        entry["review_reason"]  = "manually_verified"

        cache[db_id] = entry
        updated += 1
        print(f"    Updated: {new_row['name']} — {new_row['artist']}")

    save_json(RECORDING_CACHE_FILE, cache)
    print(f"    Done. {updated} updated, {skipped} skipped.")
    
    pairs = list(zip(rows[0::2], rows[1::2]))
    remaining_pairs = [(old, new) for old, new in pairs if new.get("confirmed", "0") != "1"]
    if len(remaining_pairs) < len(pairs):
        remaining_rows = [row for pair in remaining_pairs for row in pair] 
        with open(FAILED_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(remaining_rows)
        removed = len(pairs) - len(remaining_pairs)
        print(f"    Removed {removed} confirmed pairs from {FAILED_LOG_FILE}")


if __name__ == "__main__":

    recording_cache  = load_json(RECORDING_CACHE_FILE)

    print("🗿  Reading manual review log...")
    with open(FAILED_LOG_FILE, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"    Found {len(rows)/2} entries to update")
    manual_repair(recording_cache, rows)
    print("🗿  Manual repair completed!")