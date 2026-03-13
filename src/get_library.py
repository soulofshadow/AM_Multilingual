import subprocess
import csv
import os
from .utils import MUSIC_LIBRARY_FILE, FIELDS

APPLESCRIPT = '''
on joinList(lst)
    set AppleScript's text item delimiters to "|||"
    set str to lst as string
    set AppleScript's text item delimiters to ""
    return str
end joinList

tell application "Music"
    set lib to library playlist 1
    set dbIDs to persistent ID of every track of lib
    set tNames to name of every track of lib
    set tArtists to artist of every track of lib
    set tAlbumArtists to album artist of every track of lib
    set tAlbums to album of every track of lib
    set sNames to sort name of every track of lib
    set sArtists to sort artist of every track of lib
    set sAlbumArtists to sort album artist of every track of lib
    set sAlbums to sort album of every track of lib
end tell

set output to joinList(dbIDs) & "<END_LIST>" & joinList(tNames) & "<END_LIST>" & joinList(tArtists) & "<END_LIST>" & joinList(tAlbumArtists) & "<END_LIST>" & joinList(tAlbums) & "<END_LIST>" & joinList(sNames) & "<END_LIST>" & joinList(sArtists) & "<END_LIST>" & joinList(sAlbumArtists) & "<END_LIST>" & joinList(sAlbums)

return output
'''

def fetch_library() -> list[dict]:
    result = subprocess.run(
        ["osascript", "-e", APPLESCRIPT],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr}")

    # 1. Split <END_LIST> 
    lists_str = result.stdout.strip().split("<END_LIST>")
    if len(lists_str) != 9:
        raise RuntimeError("Unexpected number of columns returned from AppleScript")

    # 2. Split ||| to get 9 lists of track info
    columns = [lst.split("|||") for lst in lists_str]

    tracks = []
    num_tracks = len(columns[0]) 
    
    # 3. Combine the 9 columns into a list of track dictionaries
    for i in range(num_tracks):
        track = {}
        for j, field in enumerate(FIELDS):
            val = columns[j][i] if i < len(columns[j]) else ""
            if val == "missing value":
                val = ""
                
            track[field] = val.strip()
            
        tracks.append(track)

    return tracks

def save_csv(tracks, path="default.csv"):
    if os.path.exists(path):
        os.remove(path)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(tracks)
    print(f"    Saved {len(tracks)} tracks to {path}")

if __name__ == "__main__":
    print("📚  Reading library (Bulk Extraction mode)...")
    tracks = fetch_library()
    print(f"    Found {len(tracks)} tracks")
    save_csv(tracks, MUSIC_LIBRARY_FILE)
    print("📚  Library saved!")