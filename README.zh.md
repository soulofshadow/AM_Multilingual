# 🎵 Apple Music Metadata Fixer

**[English](README.md) | [中文](README.zh.md)**

这是一个利用 **Gemini API** 和 **MusicBrainz** 自动修复并本地化 Apple Music 资料库元数据（歌曲名、歌手、专辑）的工具。

适用于您的资料库中包含以下情况：
- 拼音/罗马音化的名称（例如：`Zitan Qi` → `祁紫檀`）
- 错误的语言元数据（例如：中文歌曲显示为英文标题）
- 缺失或错误的“专辑艺人 (Album Artist)”字段
- 来自亚洲市场的歌曲带有不准确的地区元数据

---

## ✨ 核心特性

- 通过 AppleScript 导出完整的 Apple Music 资料库
- 使用 Gemini AI 将元数据纠正为**原始语言**（付费版支持使用 Google 搜索获取最新发行的歌曲信息）
- 识别每首歌曲的**原始发行国家/地区**
- 为中日韩文名称生成罗马拼音排序字段（拼音、罗马音等）
- 通过 AppleScript 将修正后的元数据写回 Music.app
- 增量处理 —— 自动跳过已修复的曲目
- 集成 MusicBrainz 用于艺人名称本地化
- 针对低置信度修复的“手动审核”工作流
- 在本地缓存所有结果以避免重复调用 API（仓库中也分享了我的 MusicBrainz 缓存和规范化的艺人名称缓存）
- **🤖 通过 macOS 快捷指令实现“零打扰”全自动化运行**

---

## 预览

![Preview](https://github.com/user-attachments/assets/0a1f32db-0fe2-4de3-81a2-347e53f6536f)

---

## 📋 环境要求

- 带有 **音乐 (Music.app)** 的 macOS
- Python 3.12+
- 一个 **Gemini API 密钥** —— 可以在 [aistudio.google.com](https://aistudio.google.com) 免费获取

安装依赖：

```bash
pip3 install google-genai tqdm python-dotenv opencc-python-reimplemented pypinyin pykakasi hangul-romanize
```

---

## 🚀 快速开始 (终端运行)

### 1. 克隆仓库

```bash
git clone https://github.com/soulofshadow/AM_Multilingual.git
cd AM_Multilingual
```

### 2. 配置环境

在项目根目录创建一个 `.env` 文件：

```text
GEMINI_API_KEY=your_api_key_here
PAID_USER = false  # 如果使用付费版 Gemini API 密钥，请设置为 true
```
- `False` (免费额度): **每天 500 次请求 (500 RPD)**
- `True` (付费额度): 支持通过 Google 搜索获取最新发行的歌曲信息

### 3. 运行一键修复脚本

```bash
chmod +x scripts/fix_gemini.sh
./scripts/fix_gemini.sh
```

或者逐步运行每个脚本：

```bash
python3 -m src.get_library      # 第一步: 导出资料库
python3 -m src.gemini_repair    # 第二步: 修复元数据
python3 -m src.write_library    # 第三步: 写回 Music.app
```

> ⚠️ 每次运行写回脚本之前，请务必**备份您的资料库**。

---

## 🔍 手动审核工作流

Gemini 不太确定的曲目将被标记为 `needs_review`，并保存到 `data/needs_review.csv` 中，而不会被自动写回。请使用此工作流来处理它们：

### 第一步 — 检查与确认
打开 `data/needs_review.csv` 并检查每一行。
当您验证或更正了某一行后，将其中的 `confirmed` 的值从 `0` 改为 `1`。如果保留 `confirmed = 0`，程序将跳过该行，并将其保留到下一次审核。

### 第二步 — 应用手动修正
通过终端运行：
```bash
./scripts/fix_manual.sh
```
所有已确认的曲目现在都将被写回资料库。

---

## 🤖 全自动化工作流 (macOS 快捷指令)

为了实现真正的“无人值守”体验，您可以将此工具与 macOS 快捷指令集成。它会在后台静默监听加入 Apple Music 资料库的新歌并自动修复，只有在需要手动审核时才会通知您。

### 1. 安装快捷指令
点击以下链接在您的 Mac 上安装预设好的快捷指令：
- **[Apple Music Fixer](https://www.icloud.com/shortcuts/7cf162e4b99a4166b87da07e3e13df92)** (运行主自动化流程)
- **[Apple Music Fixer - Manual](https://www.icloud.com/shortcuts/670030e9d3bc481e8c32d3eec82373af)** (运行手动审核后的写回流程)

**请务必修改这些快捷指令中“运行 Shell 脚本”操作的路径，使其与您实际的项目目录路径一致。**

**(注意：确保您的 `.env` 文件中包含了您的 `PATH` 环境变量，以便后台脚本能够找到您的 Python 环境。您可以在终端运行 `which python3` 来获取路径)。**

### 2. 设置后台触发器

![Preview](https://github.com/user-attachments/assets/8e08f4b1-2cc8-4374-874a-709b6df6de0d)

为了让它在您添加歌曲时完全自动运行：
1. 打开 Mac 上的 **快捷指令** App，进入 **自动化 (Automation)**。
2. 创建一个新的 **文件夹 (Folder)** 自动化。
3. 选择您的 Apple Music 媒体文件夹（通常是 `~/Music/Music/Media/Media.localized`）。
4. 勾选 **添加 (Added)** 和 **修改 (Modified)**。
5. 设置为 **立即运行 (Run Immediately)**（无需确认）。
6. 选择运行 **Apple Music Fixer** 快捷指令。

**工作原理：** 每当您添加一首新歌时，系统会检测到文件变化并触发修复工具。如果所有歌曲都成功修复，它会在后台静默完成。如果有任何歌曲未能通过置信度检查，系统会弹出通知提醒您去查看 `needs_review.csv`。

---

## 📁 文件结构

```text
.
├── src/
│   ├── __init__.py
│   ├── get_library.py      # 通过 AppleScript 从 Music.app 导出资料库
│   ├── gemini_repair.py    # 使用 Gemini API 修复元数据
│   ├── manual_repair.py    # 从 needs_review.csv 应用手动修复
│   ├── write_library.py    # 将修正后的元数据写回 Music.app
│   ├── musicbrain.py       # MusicBrainz 艺人名称本地化
│   └── utils.py            # 共享工具类（缓存、速率限制、罗马音转换）
├── scripts/
│   ├── fix_gemini.sh             # 终端一键修复脚本
│   ├── fix_manual.sh             # 终端一键修复脚本（在手动验证后使用）
│   ├── shortcuts_gemini.sh       # 由快捷指令触发的自动化脚本
│   └── shortcuts_manual.sh       # 用于手动审核写回的自动化脚本
├── cache/
│   ├── recording_cache.json  # 已修正元数据的缓存
│   ├── artist_cache.json     # MusicBrainz 艺人本地化结果缓存
│   ├── mb_cache.json         # MusicBrainz 查询缓存
│   └── fixed_cache.json      # 用于增量处理的记录缓存
├── data/
│   ├── music_library.csv     # 从 Music.app 导出的原始资料库
│   └── needs_review.csv      # 标记为需要手动审核的曲目
├── README.md                 
└── .env                      # 您的 API 密钥和 PATH（请勿提交到 Git）
```

---

## 🗃️ 缓存格式

处理结果存储在 `cache/recording_cache.json` 中：

```json
"689E899A6FBA5E01": {                  // Music.app 中的数据库 ID     
    "name":             "コイワズライ",  // Music.app 中的原名 (保留)
    "artist":           "Aimer",       // Music.app 中的原艺人 (保留)
    "album_artist":     "Aimer",       // Music.app 中的原专辑艺人 (保留)
    "album":            "Sun Dance",   // Music.app 中的原专辑 (保留)

    "sort_name":        "Koiwazurai",  // 罗马音排序字段 (已修正)
    "sort_artist":      "Aimer",       // 罗马音排序字段 (已修正)
    "sort_album_artist":"Aimer",       // 罗马音排序字段 (已修正)
    "sort_album":       "Sun Dance",   // 罗马音排序字段 (已修正)

    "song_name":        "コイワズライ",  // Gemini 返回的修正名称 (新增字段)
    "artist_name":      "Aimer",       // Gemini 返回的修正艺人 (新增字段)
    "album_artist_name":"Aimer",       // Gemini 返回的修正专辑艺人 (新增字段)
    "album_name":       "Sun Dance",   // Gemini 返回的修正专辑 (新增字段)
    "country":          "Japan",       // Gemini 识别的原始发行国家 (新增字段)
    "language":         "Japanese",    // Gemini 识别的原始语言 (新增字段)
    "needs_review":     false          // 结果是否需要手动审核 (新增字段)
}
```

---

## 🌏 支持语言

该工具可以正确处理以下语言的元数据：
- 简体中文
- 繁体中文
- 日语 (日本語)
- 韩语 (한국어)
- 英语及其他拉丁字母语言

---

## ⚠️ 注意事项

- 在运行 `write_library.py` 之前，务必**备份您的资料库**。
- MusicBrainz API 具有严格的 **1 请求/秒** 的速率限制 —— 本工具会自动处理此限制。
- **Gemini 倾向于返回官方的标准专辑名称，并会自动移除版本标签，例如 `(Deluxe)`、`- Single`、`- EP`。**

---

## 📄 许可证

MIT
