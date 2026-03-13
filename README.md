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
- **🤖 Zero-disturbance full automation via macOS Shortcuts**

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

## 🚀 Quick Start (Terminal)

### 1. Clone the repository

```bash
git clone https://github.com/soulofshadow/AM_Multilingual.git
cd AM_Multilingual
```

### 2. Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
PAID_USER = false  # Set to true if using a paid Gemini API key
```
- `False` (free tier): **500 RPD**
- `True` (paid tier): supports Google Search grounding for newer releases

### 3. Run the one-click fix script

```bash
chmod +x scripts/fix_gemini.sh
./scripts/fix_gemini.sh
```

Or run each step individually:

```bash
python3 -m src.get_library      # Step 1: Export library
python3 -m src.gemini_repair    # Step 2: Fix metadata
python3 -m src.write_library    # Step 3: Write back to Music.app
```

> ⚠️ Always **back up your library** before running the write-back scripts.

---

## 🔍 Manual Review Workflow

Tracks where Gemini is uncertain are flagged as `needs_review` and saved to `data/needs_review.csv` instead of being written back automatically. Use this workflow to handle them:

### Step 1 — Review and Confirm
Open `data/needs_review.csv` and check each row.
Change `confirmed` from `0` to `1` when you have verified or corrected the row. Leave `confirmed = 0` to skip a row and keep it pending for next time.

### Step 2 — Apply manual corrections
You can simply click and run the **Apple Music Fixer - Manual** Shortcut you installed earlier. 

Alternatively, run it via terminal:
```bash
./scripts/fix_manual.sh
```
All confirmed tracks are now included in the write-back.

---

## 🤖 Fully Automated Workflow (macOS Shortcuts)

For a truly hands-off experience, you can integrate this tool with macOS Shortcuts. It will automatically listen for new songs added to your Apple Music library, fix them silently in the background, and only notify you if manual review is needed.

### 1. Install the Shortcuts
Click the links below to install the ready-made Shortcuts on your Mac:
- **[Apple Music Fixer](https://www.icloud.com/shortcuts/7cf162e4b99a4166b87da07e3e13df92)** (Runs the main automation)
- **[Apple Music Fixer - Manual](https://www.icloud.com/shortcuts/670030e9d3bc481e8c32d3eec82373af)** (Runs the manual review write-back)

**Make sure to edit the "Run Shell Script" action in these Shortcuts to match your actual project directory path.**

**(Note: make sure your `.env` also includes your `PATH` variable so the background script can locate your Python environment). You can run `which python3` to get the `PATH`.**

### 2. Set up the Background Trigger

![Preview](https://github.com/user-attachments/assets/8e08f4b1-2cc8-4374-874a-709b6df6de0d)

To make it run entirely on its own whenever you add a song:
1. Open the **Shortcuts** app on your Mac and go to **Automation**.
2. Create a new **Folder** automation.
3. Choose your Apple Music Media folder (Usually `~/Music/Music/Media/Media.localized`).
4. Check **Added** and **Modified**.
5. Set it to **Run Immediately** (no confirmation).
6. Select the **Apple Music Fixer** shortcut to run.

**How it works:** Whenever you add a new song, the system detects the file change and triggers the fixer. If everything is successfully fixed, it finishes silently. If any song fails the confidence check, a system notification will pop up reminding you to review the `needs_review.csv`. 

---

## 📁 File Structure

```text
.
├── src/
│   ├── __init__.py
│   ├── get_library.py      # Export library from Music.app via AppleScript
│   ├── gemini_repair.py    # Fix metadata using Gemini API
│   ├── manual_repair.py    # Apply manual corrections from needs_review.csv
│   ├── write_library.py    # Write corrected metadata back to Music.app
│   ├── musicbrain.py       # MusicBrainz artist name localization
│   └── utils.py            # Shared helpers (cache, rate limiting, romanization)
├── scripts/
│   ├── fix_gemini.sh             # Terminal one-click fix script
│   ├── fix_manual.sh             # Terminal one-click fix script (after manual verification)
│   ├── shortcuts_gemini.sh       # Automation script triggered by Shortcuts
│   └── shortcuts_manual.sh       # Automation script for manual review write-back
├── cache/
│   ├── recording_cache.json  # Cached corrected metadata
│   ├── artist_cache.json     # Cached MusicBrainz artist localization results
│   ├── mb_cache.json         # Cached MusicBrainz lookups
│   └── fixed_cache.json      # Cached for incremental processing
├── data/
│   ├── music_library.csv     # Raw exported library from Music.app
│   └── needs_review.csv      # Tracks flagged for manual review
├── README.md
└── .env                      # Your API key and PATH (do not commit)
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