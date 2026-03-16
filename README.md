# 🎵 Apple Music Metadata Fixer

**[English](README.md) | [中文](README.zh.md)**

A tool to automatically fix and localize metadata (song name, artist, album) in your Apple Music library using the **Gemini API** and **MusicBrainz**.

Useful if your library contains:
- Transliterated names (e.g., `Zitan Qi` → `祁紫檀`)
- Wrong language metadata (e.g., Chinese songs displayed with English titles)
- Missing or incorrect "Album Artist" fields
- Songs from Asian markets with inaccurate region metadata

---

## ✨ Features

- **🤖 "Zero-disturbance" full automation via macOS Shortcuts**
- Corrects metadata to the **original language** using Gemini AI (Paid tier supports Google Search grounding for newly released tracks)
- Generates romanized sort fields (pinyin, romaji, romanization) for CJK and Korean names
- Incremental processing — automatically skips already-fixed tracks
- MusicBrainz integration for artist name localization
- Manual review workflow for low-confidence corrections
- Caches all results locally to avoid redundant API calls (Also shares my MusicBrainz cache and normalized artist name cache in the repo)

---

## Preview

![Preview](https://github.com/user-attachments/assets/68954c94-0f65-4805-905e-e4dec5f3d86d)

---

## 🛠 Preparation (Required)

Before configuring the automation, you need to download the project to your local machine and set up the environment.

### 1. Requirements
- macOS with **Music.app**
- Python 3.12+
- A **Gemini API key** — free tier available at [aistudio.google.com](https://aistudio.google.com)

### 2. Download and Install Dependencies
Open your terminal and run the following commands to clone the repository and install necessary Python libraries:

```bash
git clone [https://github.com/soulofshadow/AM_Multilingual.git](https://github.com/soulofshadow/AM_Multilingual.git)

cd AM_Multilingual

pip3 install google-genai tqdm python-dotenv opencc-python-reimplemented pypinyin pykakasi hangul-romanize
```

### 3. Configure API Key and Environment Variables
Create a `.env` file in the project root and fill in your API key and Python path (for background execution by Shortcuts):

```text
GEMINI_API_KEY=your_api_key_here
PAID_USER = false  # Set to true if using a paid Gemini API key
PATH="<REPLACE_WITH_YOUR_PYTHON_DIR>:/opt/homebrew/bin:/usr/local/bin:$PATH"
```
> **💡 How to fill in the PATH? (Crucial)**
> When the macOS Shortcut runs in the background sandbox, it needs to know where your Python environment is.
> 1. In your Mac terminal, type and press Enter: `dirname "$(command -v python3)"`
> 2. The terminal will output a **directory path** (e.g., python3=`/opt/homebrew/opt/python@3.12/libexec/bin` or `/usr/local/bin`).
> 3. Replace `<REPLACE_WITH_YOUR_PYTHON_DIR>` in the code above with this exact path.

*(Note: `PAID_USER = false` uses the free tier with 500 requests per day; setting it to `true` enables Google Search grounding to fetch info for the latest releases.)*

---

## 🤖 Recommended: Fully Automated Workflow (macOS Shortcuts)

For a truly "hands-off" experience, it is highly recommended to integrate this tool with macOS Shortcuts. It will silently listen for new songs added to your Apple Music library in the background and fix them automatically, only bothering you when a manual review is needed.

### Step 1: Install the Shortcuts
Click the links below to install the ready-made Shortcuts on your Mac:
- **[Apple Music Fixer](https://www.icloud.com/shortcuts/7cf162e4b99a4166b87da07e3e13df92)** (Runs the main automation process)
- **[Apple Music Fixer - Manual](https://www.icloud.com/shortcuts/670030e9d3bc481e8c32d3eec82373af)** (Runs the write-back process after manual review)

> **Please make sure to edit both shortcuts and modify the `cd` path to match the actual local directory path where you cloned this project.**

### Step 2: Set up the Background Trigger

![Preview](https://github.com/user-attachments/assets/8e08f4b1-2cc8-4374-874a-709b6df6de0d)

To make it run entirely on its own whenever you add a song:
1. Open the **Shortcuts** app on your Mac and go to **Automation**.
2. Create a new **Folder** automation.
3. Choose your Apple Music Media folder (Usually `~/Music/Music/Media/Media.localized` or `~/Music/Music/Media`).
4. Check **Added** and **Modified**.
5. Set it to **Run Immediately** (no confirmation).
6. Select the **Apple Music Fixer** shortcut you just installed to run.

**🎉 All done!** Now, whenever you add a new song, the system detects the file change and silently fixes it in the background. If entirely successful, there will be no prompts; if any songs fail the AI confidence check, a system notification will pop up reminding you to check `needs_review.csv`.

---

## 🔍 Manual Review Workflow

Tracks where Gemini is uncertain are flagged as `needs_review` and saved to `data/needs_review.csv` instead of being written back automatically. Upon receiving the system notification, use this workflow to handle them:

### 1. Review and Confirm
Open `data/needs_review.csv` and check each row.
Change the value of `confirmed` from `0` to `1` when you have verified or corrected a row. If you leave `confirmed = 0`, the program will skip that row and keep it pending for the next review.

### 2. Apply Manual Corrections
Once you finish editing, simply click to run the **Apple Music Fixer - Manual** shortcut you installed earlier (or run `./scripts/fix_manual.sh` in the terminal). All confirmed tracks will now be safely written back to the library.

---

## 💻 Alternative: Run Manually via Terminal

If you prefer not to use Shortcuts for background execution, you can always manually trigger the fix in the terminal:

### One-Click Fix All
```bash
chmod +x scripts/fix_gemini.sh
./scripts/fix_gemini.sh
```

### Or Run Step-by-Step
```bash
python3 -m src.get_library      # Step 1: Export library
python3 -m src.gemini_repair    # Step 2: Fix metadata
python3 -m src.write_library    # Step 3: Write back to Music.app
```
> ⚠️ Always **back up your library** before running the write-back scripts.

---

## 📁 File Structure

```text
.
├── src/
│   ├── __init__.py
│   ├── get_library.py      # Exports library from Music.app via AppleScript
│   ├── gemini_repair.py    # Fixes metadata using Gemini API
│   ├── manual_repair.py    # Applies manual corrections from needs_review.csv
│   ├── write_library.py    # Writes corrected metadata back to Music.app
│   ├── musicbrain.py       # MusicBrainz artist name localization
│   └── utils.py            # Shared helpers (cache, rate limiting, romanization)
├── scripts/
│   ├── fix_gemini.sh             # Terminal one-click fix script
│   ├── fix_manual.sh             # Terminal write-back script after manual validation
│   ├── shortcuts_gemini.sh       # Main automation script called by Shortcuts in background
│   └── shortcuts_manual.sh       # Manual review write-back script called by Shortcuts
├── cache/
│   ├── recording_cache.json  # Cached corrected metadata
│   ├── artist_cache.json     # Cached MusicBrainz artist localization results
│   ├── mb_cache.json         # Cached MusicBrainz lookups
│   └── fixed_cache.json      # Cache used for incremental processing
├── data/
│   ├── music_library.csv     # Raw exported library from Music.app
│   └── needs_review.csv      # Tracks flagged for manual review
├── README.md                 
└── .env                      # Your API key and PATH (do not commit to Git)
```

---

## 🗃️ Cache Format

Processed results are stored in `cache/recording_cache.json`:

```json
"689E899A6FBA5E01": {                  // persistence ID from Music.app     
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

This tool correctly handles metadata in the following languages:
- Simplified Chinese
- Traditional Chinese
- Japanese (日本語)
- Korean (한국어)
- English and other Latin-script languages

---

## ⚠️ Notes

- Always **back up your library** before running `write_library.py`.
- Tracks are matched using the `persistence ID` from Music.app. Re-importing a track will change its ID and require re-processing.
- The `cache/recording_cache.json`, `data/`, and `.env` files are ignored by gitignore by default to protect your personal data and API keys.
- MusicBrainz API has a strict rate limit of **1 request/second** — this tool handles the limitation automatically.
- **Gemini prefers to return official standard album names and will automatically remove edition tags such as `(Deluxe)`, `- Single`, and `- EP`.**

---

## 📄 License

MIT
