import subprocess
import csv

APPLESCRIPT = '''
tell application "Music"
    set output to ""
    set allTracks to every track of library playlist 1
    repeat with t in allTracks
        set dbID        to database ID of t as string
        set tName       to name of t as string
        set tArtist     to artist of t as string
        set tAlbumArtist to album artist of t as string
        set tAlbum      to album of t as string
        set sName       to sort name of t as string
        set sArtist     to sort artist of t as string
        set sAlbumArtist to sort album artist of t as string
        set sAlbum      to sort album of t as string
        set output to output & dbID & "|||" & tName & "|||" & tArtist & "|||" & tAlbumArtist & "|||" & tAlbum & "|||" & sName & "|||" & sArtist & "|||" & sAlbumArtist & "|||" & sAlbum & "\n"
    end repeat
    return output
end tell
'''

FIELDS = [
    "db_id", "name",
    "artist", "album_artist", "album",
    "sort_name", "sort_artist", "sort_album_artist", "sort_album"
]

def fetch_library() -> list[dict]:
    result = subprocess.run(
        ["osascript", "-e", APPLESCRIPT],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript error: {result.stderr}")

    tracks = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) != len(FIELDS):
            continue
        tracks.append(dict(zip(FIELDS, parts)))
    return tracks

def save_csv(tracks, path="data/music_library_v2.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(tracks)
    print(f"✅ Saved {len(tracks)} tracks to {path}")

if __name__ == "__main__":
    print("📚 Reading library...")
    tracks = fetch_library()
    print(f"🎵 Found {len(tracks)} tracks")
    save_csv(tracks)
    for t in tracks[:5]:
        print(t)
