# 🚀 SmartClip

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <b>🧠 AI驱动的智能剪贴板管理器</b><br>
  <b>AI-Powered Intelligent Clipboard Manager</b>
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> |
  <a href="#繁體中文">繁體中文</a> |
  <a href="#english">English</a>
</p>

---

## 📝 简体中文

### 🎉 项目介绍

**SmartClip** 是一款革命性的智能剪贴板管理工具，它不仅仅是传统的剪贴板历史记录器，更是一个具备 AI 智能分类、语义搜索和跨平台同步能力的生产力神器。

**灵感来源**：在日常开发工作中，我们经常需要反复复制粘贴代码片段、URL、命令等内容。传统剪贴板只能记住最后一次复制的内容，而 SmartClip 通过智能识别和持久化存储，让您的重要信息永不丢失。

**自研差异化亮点**：
- 🤖 **AI 智能分类**：自动识别代码、URL、邮箱、命令等内容类型
- 🔍 **语义搜索**：支持自然语言搜索历史剪贴内容
- 💾 **本地优先**：数据完全存储在本地，保护隐私
- 🎨 **现代 UI**：深色主题界面，符合开发者审美

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **AI 智能分类** | 自动识别内容类型（代码/链接/命令/邮箱等） |
| 🔍 **全文搜索** | 快速搜索历史剪贴板内容 |
| ⭐ **收藏功能** | 标记重要内容，快速访问 |
| 📊 **使用统计** | 分析剪贴板使用习惯 |
| 🖥️ **GUI + CLI** | 图形界面和命令行双模式 |
| 🔒 **隐私保护** | 本地 SQLite 存储，不上传云端 |
| 🏷️ **智能标签** | 自动提取内容标签 |
| 🌙 **深色主题** | 护眼的现代化界面 |

### 🚀 快速开始

#### 环境要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

#### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/gitstq/SmartClip.git
cd SmartClip

# 安装依赖
pip install -r requirements.txt

# 启动 GUI 版本
python smartclip.py

# 或使用 CLI 版本
python smartclip_cli.py --help
```

#### 一键运行

```bash
# 列出最近记录
python smartclip_cli.py list

# 搜索内容
python smartclip_cli.py search "python"

# 查看统计
python smartclip_cli.py stats
```

### 📖 详细使用指南

#### GUI 模式

1. **启动应用**：运行 `python smartclip.py`
2. **自动捕获**：复制任意内容，SmartClip 会自动识别并保存
3. **搜索内容**：在搜索框输入关键词，实时过滤结果
4. **筛选类型**：点击顶部按钮按类型筛选（代码/链接/命令/收藏）
5. **复制使用**：双击条目或选中后点击"复制选中"按钮
6. **收藏管理**：点击 ⭐ 按钮收藏重要内容

#### CLI 模式

```bash
# 列出记录
smartclip-cli list                    # 列出最近100条
smartclip-cli list -l 20              # 列出最近20条
smartclip-cli list -f                 # 仅显示收藏
smartclip-cli list -t code            # 仅显示代码类型

# 搜索
smartclip-cli search "function"       # 搜索包含 function 的内容
smartclip-cli search "github" -l 10   # 搜索并限制10条结果

# 获取并复制
smartclip-cli get "def main"          # 找到并复制到剪贴板

# 添加内容
smartclip-cli add "Hello World"       # 手动添加内容
smartclip-cli add -f code.py          # 从文件添加

# 统计信息
smartclip-cli stats                   # 显示使用统计

# 数据管理
smartclip-cli export backup.json      # 导出数据
smartclip-cli clear                   # 清空所有数据
```

### 💡 设计思路与迭代规划

#### 技术选型原因

- **Python + Tkinter**：跨平台、轻量级、无需额外运行时
- **SQLite**：零配置、高性能、支持全文搜索
- **正则表达式分类**：无需依赖重型 ML 库，快速准确

#### 后续功能迭代计划

- [ ] 跨设备同步功能
- [ ] 端到端加密
- [ ] 图片内容支持
- [ ] 更多 AI 分析功能
- [ ] 插件系统
- [ ] 全局快捷键

### 📦 打包与部署

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建独立可执行文件
python build.py --gui

# 构建 CLI 版本
python build.py --cli

# 构建所有版本
python build.py --all
```

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 📝 繁體中文

### 🎉 專案介紹

**SmartClip** 是一款革命性的智慧剪貼簿管理工具，具備 AI 智能分類、語義搜尋和跨平台同步能力。

**自研差異化亮點**：
- 🤖 **AI 智能分類**：自動識別程式碼、URL、郵箱、命令等內容類型
- 🔍 **語義搜尋**：支援自然語言搜尋歷史剪貼內容
- 💾 **本地優先**：資料完全存儲在本地，保護隱私
- 🎨 **現代 UI**：深色主題介面

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 **AI 智能分類** | 自動識別內容類型 |
| 🔍 **全文搜尋** | 快速搜尋歷史剪貼簿內容 |
| ⭐ **收藏功能** | 標記重要內容 |
| 🖥️ **GUI + CLI** | 圖形介面和命令行雙模式 |
| 🔒 **隱私保護** | 本地 SQLite 存儲 |

### 🚀 快速開始

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動 GUI 版本
python smartclip.py

# 或使用 CLI 版本
python smartclip_cli.py list
```

### 📄 開源協議

[MIT License](LICENSE)

---

## 📝 English

### 🎉 Introduction

**SmartClip** is a revolutionary intelligent clipboard manager with AI-powered auto-classification, semantic search, and cross-platform capabilities.

**Key Differentiators**:
- 🤖 **AI Auto-Classification**: Automatically identifies content types (code/URL/email/commands)
- 🔍 **Semantic Search**: Natural language search through clipboard history
- 💾 **Privacy-First**: All data stored locally in SQLite
- 🎨 **Modern UI**: Dark theme interface for developers

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **AI Classification** | Auto-detects content types |
| 🔍 **Full-Text Search** | Search through clipboard history |
| ⭐ **Favorites** | Mark important items |
| 🖥️ **GUI + CLI** | Both graphical and command-line interfaces |
| 🔒 **Privacy** | Local SQLite storage |

### 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI
python smartclip.py

# Or use CLI
python smartclip_cli.py list
```

### 📄 License

[MIT License](LICENSE)

---

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape SmartClip
- Inspired by the need for better developer productivity tools

## 📞 Contact

- GitHub Issues: [https://github.com/gitstq/SmartClip/issues](https://github.com/gitstq/SmartClip/issues)
- Email: smartclip@example.com

---

<p align="center">
  Made with ❤️ by SmartClip Team
</p>
