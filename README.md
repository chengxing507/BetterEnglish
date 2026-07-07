# BetterEnglish · 英语默写 · English Dictation

![Platform](https://img.shields.io/badge/platform-Android-brightgreen)
![Kotlin](https://img.shields.io/badge/language-Kotlin-purple)
![Version](https://img.shields.io/badge/version-1.5.2-blue)

> **中文** — 一款轻量、高效的英语默写练习工具，帮助中小学生巩固课内单词、词组和句子。  
> **English** — A lightweight, efficient English dictation practice tool for K-12 students to reinforce vocabulary, phrases, and sentences.

---

## 📱 应用简介 · About

| 中文 | English |
|------|---------|
| **BetterEnglish（英语默写）** 是一个专为中小学生设计的英语听写/默写辅助工具。它采用 **Android WebView + 纯前端 HTML/JS** 架构，无需网络即可使用核心功能，同时也支持接入 AI API 辅助出题。 | **BetterEnglish** is an English dictation assistant designed for K-12 students. It uses an **Android WebView + pure frontend HTML/JS** architecture — core features work offline, with optional AI API integration for generating questions. |

### 核心功能 · Core Features

| 功能 | Feature | 说明 |
|------|---------|------|
| 📖 **单词默写** | Word Dictation | 支持按单元导入单词，自动朗读并默写 |
| 📝 **词组默写** | Phrase Dictation | 词组级别默写练习 |
| 💬 **句子默写** | Sentence Dictation | 整句听写，培养语感 |
| ⏱️ **倒计时** | Countdown Timer | 每题独立计时，超时自动判错 |
| 📊 **错题本** | Wrong Answer Review | 自动记录错题，支持错题重练 |
| 🤖 **AI 出题** | AI Question Generation | 可选接入 AI API 智能生成题目 |
| 📂 **导入/导出** | Import/Export | 支持 JSON 格式题目导入导出，方便分享 |
| 📈 **练习统计** | Practice Statistics | 正确率、错题分布等数据可视化 |
| 📋 **历史记录导出/导入** | History Export/Import | 支持备份和恢复所有练习记录 |
| 🔖 **题目标记** | Question Marking | 支持标记题目，结束后集中复核 |
| 📡 **局域网监督** | LAN Monitor/Supervisor | 在局域网内另一设备浏览器实时查看练习进度 |

---

## 🛠️ 技术栈 · Tech Stack

| 层次 Layer | 技术 Technology |
|------------|-----------------|
| **原生壳 Native Shell** | Kotlin + AndroidX (AppCompat, Core KTX) |
| **UI 引擎 UI Engine** | Android WebView + 纯前端 HTML/CSS/JavaScript |
| **本地存储 Local Storage** | `localStorage` (浏览器存储) |
| **数据格式 Data Format** | JSON |
| **构建工具 Build Tool** | Gradle + Kotlin DSL |
| **最低版本 Min SDK** | Android 5.0 (API 21) |
| **目标版本 Target SDK** | Android 14 (API 34) |

---

## 📦 项目结构 · Project Structure

```
BetterEnglish/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── assets/
│   │   │   │   ├── English_v1.4.4.html      # 主界面 (WebView 加载) Main UI
│   │   │   │   ├── English_v1.4.2.html      # 上一版本 Previous version
│   │   │   │   ├── English_v1.4.1.html      # 历史版本 History version
│   │   │   │   ├── oldversion/               # 历史版本存档 Archived versions
│   │   │   │   ├── unit/                     # 单元题库 (JSON) Unit question banks
│   │   │   │   ├── Seed/                     # 数据构建脚本 (Python) Data build scripts
│   │   │   │   ├── tool/                     # 辅助工具页面 Helper tools
│   │   │   │   ├── dictation_word.json       # 单词库 Word bank
│   │   │   │   └── experience.txt            # 开发修复经验记录 Dev notes
│   │   │   ├── java/com/be/app/
│   │   │   │   └── MainActivity.kt           # 唯一 Activity
│   │   │   ├── res/                          # 资源文件 Resources
│   │   │   └── AndroidManifest.xml
│   │   ├── build.gradle.kts
│   │   └── proguard-rules.pro
│   ├── build.gradle.kts                      # 顶层构建配置 Root build config
│   ├── settings.gradle.kts
│   ├── gradle.properties
│   ├── gradlew / gradlew.bat
│   └── .github/workflows/build.yml           # CI 配置 CI config
```

---

## 🚀 快速开始 · Quick Start

### 环境要求 · Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17
- Android SDK 34

### 构建运行 · Build & Run

```bash
# Clone the repository
git clone https://github.com/chengxing507/BetterEnglish.git
cd BetterEnglish

# Build with Gradle
./gradlew assembleDebug

# Or open in Android Studio and click Run
```

APK 构建产物位于 / Build output:
`app/build/outputs/apk/debug/app-debug.apk`

---

## 📖 使用指南 · Usage Guide

### 1. 导入题目数据 · Import Questions

应用内置了多个单元的题库（位于 `assets/unit/`），你也可以通过以下方式导入自定义题目：  
Built-in question banks are in `assets/unit/`. You can also import custom questions:

- **粘贴 JSON**：在首页的文本框中粘贴 JSON 数据 / Paste JSON into the text area
- **上传文件**：点击文件选择按钮上传 `.json` 文件 / Upload a `.json` file
- **AI 生成**：配置 AI API Key 后，可让 AI 生成题目 / Configure AI API Key to generate questions

### 2. 开始练习 · Start Practice

1. 选择单元 → 选择题型（单词/词组/句子）/ Select unit → choose type (word/phrase/sentence)
2. 点击「开始默写」/ Click "Start Dictation"
3. 看到题目后，在输入框中填写答案 / Read the prompt and type your answer
4. 提交后自动评分并进入下一题 / Submit for auto-grading, then next question
5. 练习完成后查看统计报告 / View the stats report when finished

### 3. 错题管理 · Wrong Answer Management

- 所有答错的题目自动进入错题本 / Wrong answers are automatically recorded
- 支持「错题重练」模式 / Supports "Retry Wrong Questions" mode
- 错题记录包含：正确答案、你的答案、错误次数 / Records include: correct answer, your answer, error count

### 5. 局域网监督 · LAN Monitor/Supervisor

练习过程中，可通过局域网内另一台设备的浏览器实时查看进度：  
Monitor practice progress in real-time from another device on the same LAN:

1. 在 App 首页「📡 局域网监督」区域，点击 **▶ 启动** / Tap **▶ Start** at the bottom of the home page
2. 记下显示的监督地址 `http://192.168.x.x:8080` / Note the monitor address shown
3. 在局域网内另一设备的浏览器中打开该地址 / Open the address in another device's browser on the same LAN
4. 页面每 2 秒自动刷新显示实时进度 / The page auto-refreshes every 2 seconds

> 💡 监看页面显示：练习模式、进度条、当前题目、正确率、错误数、错题列表
> 💡 The monitor page shows: practice mode, progress bar, current question, accuracy, wrong count, wrong answer list

### 4. 高级设置 · Advanced Settings

点击首页 **⚙️ 管理面板** 按钮进入管理面板（默认密码：`123456`），可设置：  
Click the version number **7 times** on the home page to enter the admin panel (password: `password`):

- ⏱️ 倒计时时间（单词/词组/句子分别设置）/ Countdown timer (per type)
- 🤖 AI API 配置 / AI API configuration
- 📊 数据管理（导入/导出/重置）/ Data management (import/export/reset)
- 🔄 **忽略标点符号** / **Ignore punctuation** (auto-normalize when checking answers)
- 📋 **导出错题**（结果页支持导出纯中文/纯英文/中英双语，一键复制） / **Export wrong questions** (Chinese/English/bilingual, one-click copy)
- 📤 **导出/导入历史记录** / **Export/Import practice history**

> 💡 管理面板：首页 **⚙️ 管理面板** 按钮进入（密码可在面板内修改）  
> 💡 Admin panel: Click **⚙️ Admin** button on home page (password changeable inside panel)

---

## 🔧 开发相关 · Development

### 构建题库 · Building Question Banks

项目提供 Python 脚本辅助构建题库数据 / Python scripts for building question bank data:

```bash
cd app/src/main/assets/Seed
python3 build_v3.py       # 构建 V3 格式题库 / Build V3 format
python3 build_v132.py     # 构建 V1.3.2 格式题库 / Build V1.3.2 format
python3 fix_build.py      # 修复数据问题 / Fix data issues
```

### CI/CD

GitHub Actions 配置位于 `.github/workflows/build.yml`，每次推送自动构建 APK。  
GitHub Actions workflow at `.github/workflows/build.yml` auto-builds APK on every push.

---

## 📜 版本历史 · Changelog

| 版本 Version | 日期 Date | 更新内容 Changes |
|-------------|-----------|-----------------|
| v1.5.2 | 2026-07 | 管理面板密码保护(可修改)；监督面板弹窗功能；结算面板同步显示；错题回顾格式优化(第一次/第二次+错误答案)；答题键盘新增/和—键；输入框增高；删除版本号彩蛋 / Admin panel password protection; supervisor popup; settlement sync; wrong answer format (1st/2nd attempt + wrong answer); keyboard adds / and —; taller input; removed easter egg |
| v1.5.1 | 2026-07 | 复核保留记录（展示✅复核通过/❌复核未过标记）、监看面板信息丰富（类型统计、倒计时、用时、元信息）、"我不会"在答错后仍记录跳过行为、复核Prompt严格化（拼写不一致即判错）、明确首页AI Prompt模板用途说明 / Review records preserved with pass/fail badges, richer LAN monitor (type stats, timer, elapsed, meta), skip recorded after wrong attempt, stricter review prompt, clarified AI Prompt label |
| v1.4.4 | 2026-07 | 新增历史记录导出/导入功能、每次答题重置题目标记、更新说明文档为双语 / Added history export/import, reset marked questions per session, bilingual README |
| v1.4.3 | 2026-07 | 正确率细分（单词/词组/句子）、修复复核正确后错题不移除、新增忽略标点符号开关、错题导出、历史记录回到结算页 / Accuracy breakdown by type, fix review bugs, punctuation toggle, wrong question export |
| v1.4.2 | 2026-07 | 答题光标支持、AI配置一键导入、格式转换提示词可编辑、JSON句子自动拆分、文件上传修复 / Input cursor support, AI config import, editable prompts, JSON sentence splitting, file upload fix |
| v1.4.1 | 2026-06 | 优化 UI 与倒计时体验 / UI and timer UX improvements |
| v1.4 | 2026-06 | 新增答题倒计时功能 / Added countdown timer |
| v1.3.2 | 2026-05 | 修复单引号输入问题、提前结束统计逻辑 / Fixed apostrophe input, early-end stats logic |
| v1.3 | 2026-04 | 新增 AI 出题、错题本功能 / Added AI question generation, wrong answer review |
| v1.2 | 2026-03 | 基础默写功能、单元切换 / Basic dictation, unit switching |
| v1.0 | 2026-02 | 初始版本 / Initial release |

---

## 📄 许可证 · License

本项目仅供个人学习与教育用途。  
This project is for personal learning and educational purposes only.

---

## 🙏 致谢 · Acknowledgements

- 感谢所有提供反馈和建议的用户 / Thanks to all users who provided feedback
- 感谢开源社区提供的优秀工具和库 / Thanks to the open-source community for great tools and libraries

---

*Made with ❤️ for better English learning*