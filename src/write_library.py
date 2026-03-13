import subprocess
from tqdm import tqdm
import json
from .utils import load_json, save_json
from .utils import RECORDING_CACHE_FILE, FIXED_CACHE_FILE


def update_track(db_id: str, row: dict):
    script = f'''
tell application "Music"
    set t to first track of library playlist 1 whose persistent ID is "{db_id}"
    set name of t to "{row["song_name"].replace('"', '\\"')}"
    set artist of t to "{row["artist_name"].replace('"', '\\"')}"
    set album artist of t to "{row["album_artist_name"].replace('"', '\\"')}"
    set album of t to "{row["album_name"].replace('"', '\\"')}"
    set sort name of t to "{row["sort_name"].replace('"', '\\"')}"
    set sort artist of t to "{row["sort_artist"].replace('"', '\\"')}"
    set sort album artist of t to "{row["sort_album_artist"].replace('"', '\\"')}"
    set sort album of t to "{row["sort_album"].replace('"', '\\"')}"
end tell
'''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return False
    return True

def write_back(tracks_to_write, fixed_cache):
    skipped = 0
    updated = 0
    failed = []
    
    pbar = tqdm(tracks_to_write.items(), total=len(tracks_to_write), desc="    Writing", ncols=100)
    for key, row in pbar:
        # Filter out tracks that still need review
        if row is None or row.get("needs_review") is True:
            skipped += 1
            pbar.update(1)
            continue
            
        # Start writing back to Music app
        pbar.set_postfix_str(f"{row['song_name'][:20]:<20} — {row['artist_name'][:15]:<15}")
        ok = update_track(key, row)
        if ok:
            updated += 1
            fixed_cache.add(key)
        else:
            failed.append({
                "db_id": key,
                "name": row.get("song_name", ""),
                "artist": row.get("artist_name", ""),
            })

    save_json(FIXED_CACHE_FILE, list(fixed_cache))
    print(f"    Done! Updated {updated}, skipped {skipped}")
    if failed:
        print("    Failed to update the following tracks (check track availability in Music):")
        for f in failed:
            print(f"        {f['name']} — {f['artist']} (db_id: {f['db_id']})")


if __name__ == "__main__":
    print("📚  Writing library...")
    recording_cache  = load_json(RECORDING_CACHE_FILE)
    fixed_cache:set  = set(load_json(FIXED_CACHE_FILE) or [])

    tracks_to_write = {k: v for k, v in recording_cache.items() if k not in fixed_cache}
    print(f"    Writing {len(tracks_to_write)} tracks back")
    write_back(tracks_to_write, fixed_cache)
    print("📚  Library update completed!")