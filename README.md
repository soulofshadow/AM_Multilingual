# 🎵 Apple Music Metadata Fixer

**[English](README.md) | [中文](README.zh.md)**

A tool to automatically fix and localize metadata (song name, artist, album) in your Apple Music library using the **Gemini API** and **MusicBrainz**.

Useful if your library contains:
- Transliterated names (e.g. `Zitan Qi` → `祁紫檀`)
- Wrong language metadata (e.g. Chinese songs displayed with English titles)
- Missing or incorrect album artist fields
- Songs from Asian markets with inaccurate region metadata

---

## ✨ Features

- Exports your full Apple Music library via AppleScript
- Corrects metadata to the **original language** using Gemini AI (with optional Google Search grounding for newer releases)
- Identifies the **original release country** of each song
- Generates romanized sort fields (pinyin, romaji, romanization) for CJK and Korean names
- Writes corrected metadata back to Music.app via AppleScript
- Incremental processing — already-fixed tracks are skipped automatically
- MusicBrainz integration for artist name localization
- Manual review workflow for low-confidence corrections
- Caches all results locally to avoid redundant API calls (Also shared my MusicBrainz cache and formalized artist name cache file there)

---

## Preview

![Preview](https://github.com/user-attachments/assets/0a1f32db-0fe2-4de3-81a2-347e53f6536f)

---

## 📋 Requirements

- macOS with **Music.app**
- Python 3.12+
- A **Gemini API key** — free tier available at [aistudio.google.com](https://aistudio.google.com)

Install dependencies:

```bash
pip3 install google-genai tqdm python-dotenv opencc-python-reimplemented pypinyin pykakasi hangul-romanize
```

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

In `src/utils.py`, set your tier:

```python
PAID_USER = False  # Set to True if using a paid Gemini API key
```

- `False` (free tier): uses `gemini-3.1-flash-lite-preview` — supports JSON schema output, **1,500 RPD**
- `True` (paid tier): uses `gemini-3-flash` — supports both JSON schema output **and** Google Search grounding for newer releases

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/soulofshadow/AM_Multilingual.git
cd AM_Multilingual
```

### 2. Set up your API key

```bash
cp .env.example .env
# edit .env and fill in your GEMINI_API_KEY
```

### 3. Run the one-click fix script

```bash
chmod +x fix_gemini.sh
./fix_gemini.sh
```

This runs all three steps in sequence:
1. **Export** your Music library from Music.app
2. **Fix** metadata using Gemini + MusicBrainz
3. **Write** corrected metadata back to Music.app

Or run each step individually:

```bash
python3 -m src.get_library      # Step 1: Export library
python3 -m src.gemini_repair    # Step 2: Fix metadata
python3 -m src.write_library    # Step 3: Write back to Music.app
```

> ⚠️ Always **back up your library** before running `write_library`.

---

## 🔍 Manual Review Workflow

Tracks where Gemini is uncertain are flagged as `needs_review` and saved to `data/needs_review.csv` instead of being written back automatically. Use this workflow to handle them:

### Step 1 — Review and Confirm

Open `data/needs_review.csv` and check each row:

```bash
|confirmed| Change from `0` to `1` when you have verified or corrected the row
```
Leave `confirmed = 0` to skip a row and keep it pending for next time.

### Step 2 — Apply manual corrections

```bash
python3 -m src.manual_repair
```

Rows marked `confirmed = 1` are written back to `cache/recording_cache.json` with `needs_review` cleared to `false`.

### Step 3 — Write back to Music.app

```bash
python3 -m src.write_library
```

All confirmed tracks are now included in the write-back.

---

## 📁 File Structure

```
.
├── src/
│   ├── __init__.py
│   ├── get_library.py      # Export library from Music.app via AppleScript
│   ├── gemini_repair.py    # Fix metadata using Gemini API
│   ├── manual_repair.py    # Apply manual corrections from needs_review.csv
│   ├── write_library.py    # Write corrected metadata back to Music.app
│   ├── musicbrain.py       # MusicBrainz artist name localization
│   └── utils.py            # Shared helpers (cache, rate limiting, romanization)
├── cache/
│   ├── recording_cache.json  # Cached corrected metadata
│   ├── artist_cache.json     # Cached MusicBrainz artist localization results
│   ├── mb_cache.json         # Cached MusicBrainz lookups
|   └── fixed_cache.json      # Cached for incremental processing
├── data/
│   ├── music_library.csv     # Raw exported library from Music.app
│   └── needs_review.csv      # Tracks flagged for manual review
├── fix_gemini.sh             # One-click fix script
├── fix_manual.sh             # One-click fix script (after manual verification)
├── README.md
└── .env                      # Your API key (do not commit)
```

---

## 🗃️ Cache Format

Processed results are stored in `cache/recording_cache.json`:

```json
"689E899A6FBA5E01": {                  // Database ID from Music.app     
    "name":             "コイワズライ",  // Original name from Music.app (preserved)
    "artist":           "Aimer",       // Original artist from Music.app (preserved)
    "album_artist":     "Aimer",       // Original album artist from Music.app (preserved)
    "album":            "Sun Dance",   // Original album from Music.app (preserved)

    "sort_name":        "Koiwazurai",  // Romanized sort field (corrected)
    "sort_artist":      "Aimer",       // Romanized sort field (corrected)
    "sort_album_artist":"Aimer",       // Romanized sort field (corrected)
    "sort_album":       "Sun Dance",   // Romanized sort field (corrected)

    "song_name":        "コイワズライ",  // Corrected name from Gemini (new field)
    "artist_name":      "Aimer",       // Corrected artist from Gemini (new field)
    "album_artist_name":"Aimer",       // Corrected album artist from Gemini (new field)
    "album_name":       "Sun Dance",   // Corrected album from Gemini (new field)
    "country":          "Japan",       // Original release country from Gemini (new field)
    "language":         "Japanese",    // Original language from Gemini (new field)
    "needs_review":     false          // Whether the result needs manual review (new field)
}
```

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
- The `cache/recording_cache.json`, `data/`, and `.env` files are gitignored by default to protect your personal data and API keys
- MusicBrainz API has a strict rate limit of **1 request/second** — the tool handles this automatically
- **Gemini prefers to return the official standard album name and will remove edition tags such as `(Deluxe)`, `- Single`, `- EP`**

---

## 📄 License

MIT
