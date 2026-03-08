import subprocess, csv
from src.utils import load_json, save_json


def update_track(db_id: str, row: dict):
    script = f'''
tell application "Music"
    set t to first track of library playlist 1 whose database ID is {db_id}
    set name of t to "{row["name"].replace('"', '\\"')}"
    set artist of t to "{row["artist"].replace('"', '\\"')}"
    set album artist of t to "{row["album_artist"].replace('"', '\\"')}"
    set album of t to "{row["album"].replace('"', '\\"')}"
    set sort name of t to "{row["sort_name"].replace('"', '\\"')}"
    set sort artist of t to "{row["sort_artist"].replace('"', '\\"')}"
    set sort album artist of t to "{row["sort_album_artist"].replace('"', '\\"')}"
    set sort album of t to "{row["sort_album"].replace('"', '\\"')}"
end tell
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  AppleScript error for db_id {db_id}: {result.stderr}")
        return False
    return True


def write_back(cache_file, _fixed_id_file):
    updated, failed_list, skipped = 0, [], 0
    cache = load_json(cache_file)
    _fixed_ids:set  = set(load_json(_fixed_id_file) or [])

    for cache_key, row in cache.items():
        if row is None:
            skipped += 1
            continue

        db_id = row.get("db_id")
        if not db_id:
            skipped += 1
            continue

        if db_id in _fixed_ids:
            skipped += 1
            continue

        print(f"  ✏️  Updating {db_id}: {row['name']} — {row['artist']}")
        ok = update_track(db_id, row)
        if ok:
            updated += 1
            _fixed_ids.add(db_id)
        else:
            failed_list.append(row)

    save_json(_fixed_id_file, list(_fixed_ids))

    if failed_list:
        print(f"\n❌ Failed {len(failed_list)}:")
        for r in failed_list:
            print(f"  db_id={r.get('db_id')} | {r.get('name')} — {r.get('artist')}")

        with open("data/write_back_failed.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=failed_list[0].keys())
            writer.writeheader()
            writer.writerows(failed_list)
        print(f"  💾 Saved to data/write_back_failed.csv")

    print(f"\n✅ Done! Updated {updated}, failed {len(failed_list)}, skipped {skipped}")


if __name__ == "__main__":
    print("📚 Reading library...")

    cache_file = "data/spotify_cache.json"
    fixed_id_file = "data/fixed_ids.json"

    write_back(cache_file, fixed_id_file)