# BetterEnglish · 英语默写

![Platform](https://img.shields.io/badge/platform-Android-brightgreen)
![Kotlin](https://img.shields.io/badge/language-Kotlin-purple)
![Version](https://img.shields.io/badge/version-1.4.1-blue)

> 一款轻量、高效的英语默写练习工具，帮助中小学生巩固课内单词、词组和句子。

---

## 📱 应用简介

**BetterEnglish（英语默写）** 是一个专为中小学生设计的英语听写/默写辅助工具。它采用 **Android WebView + 纯前端 HTML/JS** 架构，无需网络即可使用核心功能，同时也支持接入 AI API 辅助出题。

### 核心功能

| 功能 | 说明 |
|------|------|
| 📖 **单词默写** | 支持按单元导入单词，自动朗读并默写 |
| 📝 **词组默写** | 词组级别默写练习 |
| 💬 **句子默写** | 整句听写，培养语感 |
| ⏱️ **倒计时** | 每题独立计时，超时自动判错 |
| 📊 **错题本** | 自动记录错题，支持错题重练 |
| 🤖 **AI 出题** | 可选接入 AI API 智能生成题目 |
| 📂 **导入/导出** | 支持 JSON 格式题目导入导出，方便分享 |
| 📈 **练习统计** | 正确率、错题分布等数据可视化 |

---

## 🛠️ 技术栈

| 层次 | 技术 |
|------|------|
| **原生壳** | Kotlin + AndroidX (AppCompat, Core KTX) |
| **UI 引擎** | Android WebView + 纯前端 HTML/CSS/JavaScript |
| **本地存储** | `localStorage` (浏览器存储) |
| **数据格式** | JSON |
| **构建工具** | Gradle + Kotlin DSL |
| **最低版本** | Android 5.0 (API 21) |
| **目标版本** | Android 14 (API 34) |

---

## 📦 项目结构

```
BetterEnglish/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── assets/
│   │   │   │   ├── English_v1.4.1.html      # 主界面 (WebView 加载)
│   │   │   │   ├── English_v1.4.html          # 上一版本
│   │   │   │   ├── oldversion/                # 历史版本存档
│   │   │   │   ├── unit/                      # 单元题库 (JSON)
│   │   │   │   ├── Seed/                      # 数据构建脚本 (Python)
│   │   │   │   ├── tool/                      # 辅助工具页面
│   │   │   │   ├── dictation_word.json        # 单词库
│   │   │   │   └── experience.txt             # 开发修复经验记录
│   │   │   ├── java/com/be/app/
│   │   │   │   └── MainActivity.kt            # 唯一 Activity
│   │   │   ├── res/                           # 资源文件
│   │   │   └── AndroidManifest.xml
│   │   ├── build.gradle.kts
│   │   └── proguard-rules.pro
│   ├── build.gradle.kts                       # 顶层构建配置
│   ├── settings.gradle.kts
│   ├── gradle.properties
│   ├── gradlew / gradlew.bat
│   └── .github/workflows/build.yml            # CI 配置
```

---

## 🚀 快速开始

### 环境要求

- Android Studio Hedgehog (2023.1.1) 或更高版本
- JDK 17
- Android SDK 34

### 构建运行

```bash
# 克隆仓库
git clone https://github.com/chengxing507/BetterEnglish.git
cd BetterEnglish

# 使用 Gradle 构建
./gradlew assembleDebug

# 或者直接在 Android Studio 中打开项目，点击 Run
```

APK 构建产物位于：`app/build/outputs/apk/debug/app-debug.apk`

---

## 📖 使用指南

### 1. 导入题目数据

应用内置了多个单元的题库（位于 `assets/unit/`），你也可以通过以下方式导入自定义题目：

- **粘贴 JSON**：在首页的文本框中粘贴 JSON 数据
- **上传文件**：点击文件选择按钮上传 `.json` 文件
- **AI 生成**：配置 AI API Key 后，可让 AI 根据教材内容生成题目

### 2. 开始练习

1. 选择单元 → 选择题型（单词/词组/句子）
2. 点击「开始默写」
3. 听到/看到题目后，在输入框中填写答案
4. 提交后自动评分并进入下一题
5. 练习完成后查看统计报告

### 3. 错题管理

- 所有答错的题目自动进入错题本
- 支持「错题重练」模式
- 错题记录包含：正确答案、你的答案、错误次数

### 4. 高级设置

点击首页版本号 **7 次** 进入管理面板（密码：`password`），可设置：

- ⏱️ 倒计时时间（单词/词组/句子分别设置）
- 🤖 AI API 配置
- 📊 数据管理（导入/导出/重置）

---

## 🔧 开发相关

### 构建题库

项目提供 Python 脚本辅助构建题库数据：

```bash
cd app/src/main/assets/Seed
python3 build_v3.py       # 构建 V3 格式题库
python3 build_v132.py     # 构建 V1.3.2 格式题库
python3 fix_build.py      # 修复数据问题
```

### CI/CD

GitHub Actions 配置位于 `.github/workflows/build.yml`，每次推送自动构建 APK。

---

## 📜 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.4.1 | 2026-06 | 当前最新版，优化 UI 与倒计时体验 |
| v1.4 | 2026-06 | 新增答题倒计时功能 |
| v1.3.2 | 2026-05 | 修复单引号输入问题、提前结束统计逻辑 |
| v1.3 | 2026-04 | 新增 AI 出题、错题本功能 |
| v1.2 | 2026-03 | 基础默写功能、单元切换 |
| v1.0 | 2026-02 | 初始版本 |

---

## 📄 许可证

本项目仅供个人学习与教育用途。

---

## 🙏 致谢

- 感谢所有提供反馈和建议的用户
- 感谢开源社区提供的优秀工具和库

---

*Made with ❤️ for better English learning*