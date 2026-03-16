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

- **🤖 通过 macOS 快捷指令实现“零打扰”全自动化运行**
- 使用 Gemini AI 将元数据纠正为**原始语言**（付费版支持使用 Google 搜索获取最新发行的歌曲信息）
- 为中日韩文名称生成罗马拼音排序字段（拼音、罗马音等）
- 增量处理 —— 自动跳过已修复的曲目
- 集成 MusicBrainz 用于艺人名称本地化
- 针对低置信度修复的“手动审核”工作流
- 在本地缓存所有结果以避免重复调用 API（仓库中也分享了我的 MusicBrainz 缓存和规范化的艺人名称缓存）

---

## 预览

![Preview](https://github.com/user-attachments/assets/68954c94-0f65-4805-905e-e4dec5f3d86d)

---

## 🛠 准备工作 (必须)

在配置自动化之前，您需要先将项目下载到本地并配置好环境。

### 1. 环境要求
- 带有 **音乐 (Music.app)** 的 macOS
- Python 3.12+
- 一个 **Gemini API 密钥** —— 可以在 [aistudio.google.com](https://aistudio.google.com) 免费获取

### 2. 下载项目并安装依赖
打开终端，执行以下命令克隆仓库并安装必要的 Python 库：

```bash
git clone https://github.com/soulofshadow/AM_Multilingual.git

cd AM_Multilingual

pip3 install google-genai tqdm python-dotenv opencc-python-reimplemented pypinyin pykakasi hangul-romanize
```

### 3. 配置密钥与环境变量
在项目根目录创建一个 `.env` 文件，填入您的 API 密钥和 Python 路径（供快捷指令在后台调用时使用）：

```text
GEMINI_API_KEY=your_api_key_here
PAID_USER = false  # 如果使用付费版 Gemini API 密钥，请设置为 true
PATH="<在此替换为您的_Python_目录>:/opt/homebrew/bin:/usr/local/bin:$PATH"
```
> **💡 到底该怎么填写 PATH？（极其重要）**
> 快捷指令在后台沙盒中运行时，需要知道您的 Python 环境在哪里。
> 1. 请在您的 Mac 终端中输入并回车：`dirname "$(command -v python3)"`
> 2. 终端会输出一个**文件夹路径**（例如：python3=`/opt/homebrew/opt/python@3.12/libexec/bin` 或 `/usr/local/bin`）。
> 3. 将这个路径替换掉上面代码里的 `<在此替换为您的_Python_目录>`。

*(注：`PAID_USER = false` 为免费额度，每天 500 次请求；设置为 `true` 可支持通过 Google 搜索获取最新发行的歌曲信息。)*

---

## 🤖 推荐用法：全自动化工作流 (macOS 快捷指令)

为了实现真正的“无人值守”体验，强烈建议您将此工具与 macOS 快捷指令集成。它会在后台静默监听加入 Apple Music 资料库的新歌并自动修复，只有在需要手动审核时才会打扰您。

### 第一步：安装快捷指令
点击以下链接在您的 Mac 上安装预设好的快捷指令：
- **[Apple Music Fixer](https://www.icloud.com/shortcuts/7cf162e4b99a4166b87da07e3e13df92)** (运行主自动化流程)
- **[Apple Music Fixer - Manual](https://www.icloud.com/shortcuts/670030e9d3bc481e8c32d3eec82373af)** (运行手动审核后的写回流程)

> **请务必编辑这两个快捷指令，将其中的 `cd` 路径修改为您实际克隆该项目的本地文件夹路径。**

### 第二步：设置后台触发器

![Preview](https://github.com/user-attachments/assets/8e08f4b1-2cc8-4374-874a-709b6df6de0d)

为了让它在您每次添加歌曲时自动运行：
1. 打开 Mac 上的 **快捷指令** App，进入 **自动化 (Automation)**。
2. 创建一个新的 **文件夹 (Folder)** 自动化。
3. 选择您的 Apple Music 媒体文件夹（通常是 `~/Music/Music/Media/Media.localized` 或 `~/Music/Music/Media`）。
4. 勾选 **添加 (Added)** 和 **修改 (Modified)**。
5. 设置为 **立即运行 (Run Immediately)**（无需确认）。
6. 选择运行刚才安装的 **Apple Music Fixer** 快捷指令。

**🎉 大功告成！** 现在，每当您添加一首新歌，系统会检测到文件变化并默默在后台修复。如果完全成功，将不会有任何提示；如果有未能通过 AI 置信度检查的歌曲，系统会弹窗提醒您去查看 `needs_review.csv`。

---

## 🔍 手动审核工作流

Gemini 不太确定的曲目将被标记为 `needs_review`，并保存到 `data/needs_review.csv` 中，而不会被自动写回。收到系统通知后，请使用此工作流来处理它们：

### 1. 检查与确认
打开 `data/needs_review.csv` 并检查每一行。
当您验证或更正了某一行后，将其中的 `confirmed` 的值从 `0` 改为 `1`。如果保留 `confirmed = 0`，程序将跳过该行，并将其保留到下一次审核。

### 2. 应用手动修正
修改完成后，直接点击运行您之前安装的 **Apple Music Fixer - Manual** 快捷指令即可（也可在终端运行 `./scripts/fix_manual.sh`）。所有已确认的曲目现在都将被安全写回资料库。

---

## 💻 备选方案：通过终端手动运行

如果您不想使用快捷指令后台运行，也可以随时在终端手动触发修复：

### 一键修复全部
```bash
chmod +x scripts/fix_gemini.sh
./scripts/fix_gemini.sh
```

### 或逐步执行
```bash
python3 -m src.get_library      # 第一步: 导出资料库
python3 -m src.gemini_repair    # 第二步: 修复元数据
python3 -m src.write_library    # 第三步: 写回 Music.app
```
> ⚠️ 每次运行写回脚本之前，请务必**备份您的资料库**。

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
│   ├── fix_manual.sh             # 终端手动验证后写回的脚本
│   ├── shortcuts_gemini.sh       # 供快捷指令后台调用的自动化主脚本
│   └── shortcuts_manual.sh       # 供快捷指令调用的手动审核写回脚本
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
- 曲目是通过 Music.app 中的 `persistence ID` 进行匹配的，重新导入曲目将更改其 ID 并需要重新处理。
- `cache/recording_cache.json`、`data/` 和 `.env` 文件默认被 gitignore 忽略，以保护您的个人数据和 API 密钥。
- MusicBrainz API 具有严格的 **1 请求/秒** 的速率限制 —— 本工具会自动处理此限制。
- **Gemini 倾向于返回官方的标准专辑名称，并会自动移除版本标签，例如 `(Deluxe)`、`- Single`、`- EP`。**

---

## 📄 许可证

MIT
