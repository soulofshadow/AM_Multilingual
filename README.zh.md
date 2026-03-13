# 🎵 Apple Music 元数据修复工具

**[English](README.md) | [中文](README.zh.md)**

一个使用 **Gemini API** 和 **MusicBrainz** 自动修复并本地化 Apple Music 库中歌曲元数据（歌名、艺人、专辑）的工具。

适用于以下情况：
- 名称被音译（如 `Zitan Qi` → `祁紫檀`）
- 元数据语言错误（如中文歌曲显示为英文标题）
- 专辑艺人字段缺失或错误
- 亚洲地区歌曲的地区元数据不准确

---

## ✨ 功能特色

- 通过 AppleScript 导出完整的 Apple Music 库
- 使用 Gemini AI 将元数据还原为**原始语言**（付费版支持 Google 搜索以处理新歌）
- 识别每首歌的**原始发行国家**
- 为中文、日文、韩文名称生成罗马字拼音排序字段
- 通过 AppleScript 将修正后的元数据写回 Music.app
- 增量处理 — 已修复的曲目自动跳过
- MusicBrainz 集成，用于艺人名称本地化
- 低置信度结果的人工审核流程
- 本地缓存所有结果，避免重复调用 API（同时分享了我的 MusicBrainz 缓存和规范化艺人名称缓存）

---

## 预览

![预览](https://github.com/user-attachments/assets/0a1f32db-0fe2-4de3-81a2-347e53f6536f)

---

## 📋 环境要求

- 安装了 **Music.app** 的 macOS
- Python 3.12+
- **Gemini API Key** — 免费版可在 [aistudio.google.com](https://aistudio.google.com) 获取

安装依赖：

```bash
pip3 install google-genai tqdm python-dotenv opencc-python-reimplemented pypinyin pykakasi hangul-romanize
```

---

## ⚙️ 配置

在项目根目录创建 `.env` 文件：

```
GEMINI_API_KEY=your_api_key_here
```

在 `src/utils.py` 中设置你的账户类型：

```python
PAID_USER = False  # 付费账户设为 True
```
- `False`（免费版）：使用 `gemini-3.1-flash-lite-preview`，支持 JSON 结构化输出，**每日 1,500 次请求**
- `True`（付费版）：使用 `gemini-3-flash`，同时支持 JSON 结构化输出和 **Google 搜索**（适合处理新歌）

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/soulofshadow/AM_Multilingual.git
cd AM_Multilingual
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 GEMINI_API_KEY
```

### 3. 一键修复

```bash
chmod +x fix_gemini.sh
./fix_gemini.sh
```

脚本会依次执行以下三步：
1. **导出** Music.app 中的音乐库
2. **修复** 元数据（使用 Gemini + MusicBrainz）
3. **写回** 修正后的元数据到 Music.app

也可以单独执行每个步骤：

```bash
python3 -m src.get_library      # 第一步：导出音乐库
python3 -m src.gemini_repair    # 第二步：修复元数据
python3 -m src.write_library    # 第三步：写回 Music.app
```

> ⚠️ 运行 `write_library` 前，请务必**备份你的音乐库**。

---

## 🔍 人工审核流程

Gemini 置信度较低的结果会被标记为 `needs_review`，保存到 `data/needs_review.csv`，不会自动写回。按以下步骤处理：

### 第一步 — 在 Excel / Numbers 中审核并确认

打开 `data/needs_review.csv`，检查每一行：

```bash
`confirmed`  确认或修改完成后，将 `0` 改为 `1` 
```
保留 `confirmed = 0` 则跳过该行，留待下次处理。

### 第二步 — 应用人工修正

```bash
python3 -m src.manual_repair
```

标记为 `confirmed = 1` 的行将写回 `cache/recording_cache.json`，`needs_review` 自动清除为 `false`。

### 第三步 — 写回 Music.app

```bash
python3 -m src.write_library
```

所有已确认的曲目现在都会被写回。

---

## 📁 文件结构

```
.
├── src/
│   ├── __init__.py
│   ├── get_library.py      # 通过 AppleScript 导出 Music.app 音乐库
│   ├── gemini_repair.py    # 使用 Gemini API 修复元数据
│   ├── manual_repair.py    # 应用 needs_review.csv 中的人工修正
│   ├── write_library.py    # 将修正后的元数据写回 Music.app
│   ├── musicbrain.py       # MusicBrainz 艺人名称本地化
│   └── utils.py            # 公共工具（缓存、限速、罗马字转换）
├── cache/
│   ├── recording_cache.json  # 已处理的元数据缓存
│   ├── artist_cache.json     # MusicBrainz 艺人本地化缓存
│   ├── mb_cache.json         # MusicBrainz 查询缓存
│   └── fixed_cache.json      # 增量处理缓存
├── data/
│   ├── music_library.csv     # 从 Music.app 导出的原始音乐库
│   └── needs_review.csv      # 待人工审核的曲目
├── fix_gemini.sh             # 一键修复脚本
├── fix_manual.sh             # 一键修复脚本
├── README.md
└── .env                      # API Key（不要提交到 Git）
```

---

## 🗃️ 缓存格式

处理结果存储在 `cache/recording_cache.json` 中：

```json
"689E899A6FBA5E01": {                  // Music.app 数据库 ID     
    "name":             "コイワズライ",  // Music.app 中的原始歌名（保留）
    "artist":           "Aimer",       // Music.app 中的原始艺人名（保留）
    "album_artist":     "Aimer",       // Music.app 中的原始专辑艺人（保留）
    "album":            "Sun Dance",   // Music.app 中的原始专辑名（保留）

    "sort_name":        "Koiwazurai",  // 罗马字排序字段（已修正）
    "sort_artist":      "Aimer",       // 罗马字排序字段（已修正）
    "sort_album_artist":"Aimer",       // 罗马字排序字段（已修正）
    "sort_album":       "Sun Dance",   // 罗马字排序字段（已修正）

    "song_name":        "コイワズライ",  // Gemini 返回的修正歌名（新增字段）
    "artist_name":      "Aimer",       // Gemini 返回的修正艺人名（新增字段）
    "album_artist_name":"Aimer",       // Gemini 返回的修正专辑艺人（新增字段）
    "album_name":       "Sun Dance",   // Gemini 返回的修正专辑名（新增字段）
    "country":          "Japan",       // Gemini 识别的原始发行国家（新增字段）
    "language":         "Japanese",    // Gemini 识别的原始语言（新增字段）
    "needs_review":     false          // 是否需要人工审核（新增字段）
}
```

---

## 🌏 支持语言

本工具可正确处理以下语言的元数据：
- 简体中文（简体中文）
- 繁体中文（繁體中文）
- 日文（日本語）
- 韩文（한국어）
- 英文及其他拉丁字母语言

---

## ⚠️ 注意事项

- 运行 `write_library.py` 前，请务必**备份你的音乐库**
- 曲目通过 Music.app 的 `database ID` 匹配 — 重新导入的曲目会获得新 ID，需要重新处理
- `cache/recording_cache.json`、`data/` 和 `.env` 文件默认已加入 `.gitignore`，保护你的个人数据和 API Key
- MusicBrainz API 严格限制每秒 1 次请求，工具会自动处理
- Gemini 倾向于返回官方标准专辑名，并会去掉 `(Deluxe)`、`- Single`、`- EP` 等版本标记

---

## 📄 许可证

MIT
