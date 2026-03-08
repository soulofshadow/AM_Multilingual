# 🎵 Apple Music Metadata Fixer

A tool to automatically fix and localize metadata (song name, artist, album) in your Apple Music library using the **Gemini API** or **Spotify API**.

Useful if your library contains:
- Transliterated names (e.g. `Zitan Qi` → `祁紫檀`)
- Wrong language metadata (e.g. Chinese songs displayed with English titles)
- Missing or incorrect album artist fields
- Songs from Asian markets with inaccurate region metadata

---

## ✨ Features

- Exports your full Apple Music library via AppleScript
- Corrects metadata to the **original language** using Gemini AI
- Identifies the **original release country** of each song
- Writes corrected metadata back to Music.app via AppleScript
- Incremental processing — already-fixed tracks are skipped automatically
- Caches all results locally to avoid redundant API calls
- MusicBrainz integration for artist name localization

---

## 📋 Requirements

- macOS with **Music.app**
- Python 3.12+
- A **Gemini API key** — free tier available at [aistudio.google.com](https://aistudio.google.com)

Install dependencies:

    pip install google-generativeai

---

## 🚀 Quick Start

### 1. Clone the repository

    git clone https://github.com/soulofshadow/apple-music-metadata-fixer.git
    cd apple-music-metadata-fixer

### 2. Set up your API key

    create a `.env` file in the project root:
    GEMINI_API_KEY=your_api_key_here

### 3. Export your Music library

    python src/get_library.py

Reads your full Apple Music library via AppleScript and saves it to `data/music_library.csv`.

### 4. Fix metadata

**Recommended: Gemini**

    python src/gemini_repair.py

**Alternative: Spotify** (requires active Premium subscription on the app owner account)

    python src/spotify_repair.py

Both scripts process your library, correct each track's metadata, and save results to `data/spotify_cache.json`. Already-processed tracks listed in `data/fixed_ids.json` are automatically skipped.

> Gemini Free Tier allows **1,500 requests/day** with automatic rate limiting at 15 RPM.

### 5. Write back to Music.app

    python src/write_library.py

Writes corrected metadata back to your Apple Music library using AppleScript. Only tracks not present in `data/fixed_ids.json` will be updated. Successfully updated tracks are added to `fixed_ids.json` automatically.

---

## 📁 File Structure

    .
    ├── src/
    │   ├── get_library.py      # Export library from Music.app
    │   ├── gemini_repair.py    # Fix metadata using Gemini API (recommended)
    │   ├── spotify_repair.py   # Fix metadata using Spotify API
    │   ├── write_library.py    # Write corrected metadata back to Music.app
    │   ├── musicbrain.py       # MusicBrainz artist name localization
    │   └── utils.py            # Shared helpers (cache, JSON, rate limiting)
    ├── data/
    │   ├── music_library.csv       # Raw exported library
    │   ├── spotify_cache.json      # Cached corrected metadata
    │   ├── fixed_ids.json          # Database IDs of already-fixed tracks
    │   ├── artist_cache.json       # Cached artist localization results
    │   └── mb_cache.json           # Cached MusicBrainz lookups
    ├── README.md
    └── .env                        # Your API keys (do not commit)

---

## 🔧 API Options

| API | Availability | Notes |
|---|---|---|
| **Gemini** (recommended) | Free tier, 1,500 req/day | Best coverage for Asian music metadata |
| **Spotify** | Requires Premium | App owner must have active Premium (enforced since Feb 2026) |
| **MusicBrainz** | Completely free | Used for artist name localization, 1 req/s limit |

---

## 🌏 Supported Languages

The tool correctly handles metadata in:
- Simplified Chinese (简体中文)
- Traditional Chinese (繁體中文)
- Japanese (日本語)
- Korean (한국어)
- English and other Latin-script languages

---

## ⚠️ Notes

- Always **back up your library** before running `write_library.py`
- Tracks are matched by `database ID` from Music.app — re-importing a track will change its ID and require re-processing
- The `data/` folder and `.env` file are gitignored by default to protect your personal data and API keys

---

## 📄 License

MIT
