<div align="center">

# 🦞 DocExtract-AI-CLI

**Lightweight Terminal AI Intelligent Document Structured Extraction Engine**

**轻量级终端AI智能文档结构化提取引擎**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen)]()
[![Tests](https://img.shields.io/badge/Tests-36%20Passing-success)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

## English

### 🎉 Introduction

DocExtract-AI-CLI is a **zero-dependency**, lightweight terminal tool that transforms unstructured documents into structured data using AI. Inspired by the document processing trends from [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) and [open-notebook](https://github.com/lfnovo/open-notebook), we built a focused, single-purpose tool that solves one problem exceptionally well: **extracting structured data from documents without writing code**.

**Why DocExtract-AI-CLI?**

- 🔒 **Zero Dependencies** — Pure Python standard library, no external packages required
- 🤖 **Multi-AI Provider** — OpenAI, Ollama (local), Gemini — choose what works for you
- 📋 **Schema-Driven** — Define what to extract with JSON schemas, get validated results
- 📦 **Multi-Format Support** — PDF, DOCX, PPTX, XLSX, HTML, TXT, JSON, CSV, XML, MD
- 🎯 **Built-in Templates** — Invoice, Resume, Receipt, Business Card, Contract
- 💾 **History & Stats** — SQLite-backed extraction history with analytics
- 🖥️ **Interactive TUI** — Beautiful terminal interface for interactive use
- ⚡ **Batch Processing** — Process entire directories with progress tracking

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| **📄 Document Extraction** | Extract text from 10+ formats without external dependencies |
| **🧠 AI-Powered Extraction** | Use LLMs to intelligently parse and structure document content |
| **📐 Schema Validation** | Define extraction schemas with 11 field types and validation rules |
| **🔌 Multi-Provider** | Support for OpenAI, Ollama, and Gemini APIs |
| **📊 Batch Processing** | Process hundreds of documents in one command |
| **💾 History Tracking** | SQLite database tracks all extractions with statistics |
| **🎨 Interactive TUI** | Beautiful terminal UI for non-technical users |
| **📤 Export Formats** | JSON and CSV output for easy integration |

### 🚀 Quick Start

#### Requirements
- Python 3.8+
- API key for your chosen AI provider (or local Ollama)

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/DocExtract-AI-CLI.git
cd DocExtract-AI-CLI

# Install
pip install -e .

# Or run without installing
PYTHONPATH=src python -m docextract
```

#### Interactive Mode (TUI)

```bash
# Launch interactive terminal UI
docextract
```

#### Extract Single Document

```bash
# Extract invoice using OpenAI
docextract extract invoice.pdf \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --model gpt-4o-mini

# Extract resume using local Ollama (free!)
docextract extract resume.pdf \
  --provider ollama \
  --schema resume \
  --model llama3.2
```

#### Batch Extraction

```bash
# Process all PDFs in a directory
docextract batch ./invoices/ \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --output ./results/ \
  --format json
```

#### Test Provider Connection

```bash
docextract test --provider openai --api-key $OPENAI_API_KEY
```

### 📖 Detailed Usage Guide

#### Built-in Schemas

```bash
# List available schemas
docextract schema --list

# Show schema details
docextract schema --show invoice

# Export schema to file
docextract schema --show invoice --export invoice_schema.json
```

#### Custom Schema

Create a JSON schema file defining your extraction fields:

```json
{
  "name": "CustomInvoice",
  "description": "My custom invoice schema",
  "fields": [
    {"name": "invoice_id", "type": "string", "required": true},
    {"name": "amount", "type": "currency", "required": true},
    {"name": "date", "type": "date", "required": true}
  ]
}
```

Use it:
```bash
docextract extract doc.pdf --provider openai --api-key $KEY --schema-file my_schema.json
```

#### Supported Field Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"Hello"` |
| `integer` | Whole number | `42` |
| `float` | Decimal number | `3.14` |
| `boolean` | True/False | `true` |
| `date` | Date string | `"2024-01-15"` |
| `email` | Email address | `"user@example.com"` |
| `url` | Web URL | `"https://example.com"` |
| `phone` | Phone number | `"+1-234-567-8900"` |
| `currency` | Monetary value | `"$1,234.56"` |
| `list` | Array of values | `["a", "b"]` |
| `object` | Nested object | `{"name": "John"}` |

#### View History & Statistics

```bash
# View recent extractions
docextract history --limit 20

# View statistics
docextract stats

# Export history to CSV
docextract history --export results.csv
```

### 💡 Design Philosophy

**Single Purpose, Done Well**

Unlike large frameworks like PaddleOCR (80K⭐, heavy dependencies) or open-notebook (25K⭐, full-stack app), DocExtract-AI-CLI focuses on one task: **structured data extraction**. This makes it:

- **Lightweight**: Zero external dependencies
- **Fast**: Minimal overhead, direct processing
- **Portable**: Works anywhere Python runs
- **Composable**: Easy to integrate into pipelines

**Schema-First Approach**

Instead of training custom models or writing complex parsers, you describe what you want in a schema. The AI does the hard work of understanding the document and extracting the right information.

### 📦 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Run linting
make lint

# Clean build artifacts
make clean
```

### 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 简体中文

### 🎉 项目介绍

DocExtract-AI-CLI 是一个**零依赖**的轻量级终端工具，使用AI将非结构化文档转换为结构化数据。受 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 和 [open-notebook](https://github.com/lfnovo/open-notebook) 的文档处理趋势启发，我们构建了一个专注的单一用途工具，出色地解决了一个问题：**无需编写代码即可从文档中提取结构化数据**。

**为什么选择 DocExtract-AI-CLI？**

- 🔒 **零依赖** — 纯Python标准库，无需外部包
- 🤖 **多AI提供商** — OpenAI、Ollama（本地）、Gemini — 选择适合您的
- 📋 **Schema驱动** — 使用JSON Schema定义提取内容，获取验证结果
- 📦 **多格式支持** — PDF、DOCX、PPTX、XLSX、HTML、TXT、JSON、CSV、XML、MD
- 🎯 **内置模板** — 发票、简历、收据、名片、合同
- 💾 **历史与统计** — SQLite支持的提取历史与分析
- 🖥️ **交互式TUI** — 美观的终端界面，适合非技术用户
- ⚡ **批量处理** — 带进度跟踪的整目录处理

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **📄 文档提取** | 从零依赖的10+格式中提取文本 |
| **🧠 AI智能提取** | 使用LLM智能解析和结构化文档内容 |
| **📐 Schema验证** | 使用11种字段类型和验证规则定义提取Schema |
| **🔌 多提供商** | 支持OpenAI、Ollama和Gemini API |
| **📊 批量处理** | 一条命令处理数百个文档 |
| **💾 历史跟踪** | SQLite数据库跟踪所有提取和统计信息 |
| **🎨 交互式TUI** | 美观的终端UI |
| **📤 导出格式** | JSON和CSV输出，便于集成 |

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- 所选AI提供商的API密钥（或本地Ollama）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/DocExtract-AI-CLI.git
cd DocExtract-AI-CLI

# 安装
pip install -e .

# 或不安装直接运行
PYTHONPATH=src python -m docextract
```

#### 交互模式（TUI）

```bash
# 启动交互式终端界面
docextract
```

#### 提取单个文档

```bash
# 使用OpenAI提取发票
docextract extract invoice.pdf \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --model gpt-4o-mini

# 使用本地Ollama提取简历（免费！）
docextract extract resume.pdf \
  --provider ollama \
  --schema resume \
  --model llama3.2
```

#### 批量提取

```bash
# 处理目录中所有PDF
docextract batch ./invoices/ \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --output ./results/ \
  --format json
```

#### 测试提供商连接

```bash
docextract test --provider openai --api-key $OPENAI_API_KEY
```

### 📖 详细使用指南

#### 内置Schema

```bash
# 列出可用Schema
docextract schema --list

# 显示Schema详情
docextract schema --show invoice

# 导出Schema到文件
docextract schema --show invoice --export invoice_schema.json
```

#### 自定义Schema

创建JSON Schema文件定义您的提取字段：

```json
{
  "name": "CustomInvoice",
  "description": "我的自定义发票Schema",
  "fields": [
    {"name": "invoice_id", "type": "string", "required": true},
    {"name": "amount", "type": "currency", "required": true},
    {"name": "date", "type": "date", "required": true}
  ]
}
```

使用它：
```bash
docextract extract doc.pdf --provider openai --api-key $KEY --schema-file my_schema.json
```

#### 支持的字段类型

| 类型 | 描述 | 示例 |
|------|------|---------|
| `string` | 文本值 | `"Hello"` |
| `integer` | 整数 | `42` |
| `float` | 小数 | `3.14` |
| `boolean` | 布尔值 | `true` |
| `date` | 日期字符串 | `"2024-01-15"` |
| `email` | 邮箱地址 | `"user@example.com"` |
| `url` | 网址 | `"https://example.com"` |
| `phone` | 电话号码 | `"+1-234-567-8900"` |
| `currency` | 货币值 | `"$1,234.56"` |
| `list` | 数组 | `["a", "b"]` |
| `object` | 嵌套对象 | `{"name": "John"}` |

#### 查看历史与统计

```bash
# 查看最近提取记录
docextract history --limit 20

# 查看统计信息
docextract stats

# 导出历史到CSV
docextract history --export results.csv
```

### 💡 设计理念

**单一用途，做到极致**

与PaddleOCR（80K⭐，重依赖）或open-notebook（25K⭐，全栈应用）等大型框架不同，DocExtract-AI-CLI专注于一个任务：**结构化数据提取**。这使其：

- **轻量级**：零外部依赖
- **快速**：最小开销，直接处理
- **可移植**：任何能运行Python的地方都能工作
- **可组合**：易于集成到流水线中

**Schema优先方法**

无需训练自定义模型或编写复杂解析器，您只需在Schema中描述所需内容。AI负责理解文档并提取正确信息。

### 📦 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
make test

# 运行测试（带覆盖率）
make test-cov

# 格式化代码
make format

# 运行代码检查
make lint

# 清理构建产物
make clean
```

### 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 📄 开源协议

本项目采用 MIT 协议 - 详见 [LICENSE](LICENSE) 文件。

---

## 繁體中文

### 🎉 專案介紹

DocExtract-AI-CLI 是一個**零依賴**的輕量級終端工具，使用AI將非結構化文件轉換為結構化資料。受 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 和 [open-notebook](https://github.com/lfnovo/open-notebook) 的文件處理趨勢啟發，我們構建了一個專注的單一用途工具，出色地解決了一個問題：**無需編寫程式碼即可從文件中提取結構化資料**。

**為什麼選擇 DocExtract-AI-CLI？**

- 🔒 **零依賴** — 純Python標準庫，無需外部套件
- 🤖 **多AI提供商** — OpenAI、Ollama（本地）、Gemini — 選擇適合您的
- 📋 **Schema驅動** — 使用JSON Schema定義提取內容，獲取驗證結果
- 📦 **多格式支援** — PDF、DOCX、PPTX、XLSX、HTML、TXT、JSON、CSV、XML、MD
- 🎯 **內建模板** — 發票、履歷、收據、名片、合約
- 💾 **歷史與統計** — SQLite支援的提取歷史與分析
- 🖥️ **互動式TUI** — 美觀的終端介面，適合非技術用戶
- ⚡ **批次處理** — 帶進度追蹤的整目錄處理

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **📄 文件提取** | 從零依賴的10+格式中提取文字 |
| **🧠 AI智慧提取** | 使用LLM智慧解析和結構化文件內容 |
| **📐 Schema驗證** | 使用11種欄位類型和驗證規則定義提取Schema |
| **🔌 多提供商** | 支援OpenAI、Ollama和Gemini API |
| **📊 批次處理** | 一條命令處理數百個文件 |
| **💾 歷史追蹤** | SQLite資料庫追蹤所有提取和統計資訊 |
| **🎨 互動式TUI** | 美觀的終端UI |
| **📤 匯出格式** | JSON和CSV輸出，便於整合 |

### 🚀 快速開始

#### 環境要求
- Python 3.8+
- 所選AI提供商的API金鑰（或本地Ollama）

#### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/DocExtract-AI-CLI.git
cd DocExtract-AI-CLI

# 安裝
pip install -e .

# 或不安裝直接執行
PYTHONPATH=src python -m docextract
```

#### 互動模式（TUI）

```bash
# 啟動互動式終端介面
docextract
```

#### 提取單個文件

```bash
# 使用OpenAI提取發票
docextract extract invoice.pdf \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --model gpt-4o-mini

# 使用本地Ollama提取履歷（免費！）
docextract extract resume.pdf \
  --provider ollama \
  --schema resume \
  --model llama3.2
```

#### 批次提取

```bash
# 處理目錄中所有PDF
docextract batch ./invoices/ \
  --provider openai \
  --api-key $OPENAI_API_KEY \
  --schema invoice \
  --output ./results/ \
  --format json
```

#### 測試提供商連線

```bash
docextract test --provider openai --api-key $OPENAI_API_KEY
```

### 📖 詳細使用指南

#### 內建Schema

```bash
# 列出可用Schema
docextract schema --list

# 顯示Schema詳情
docextract schema --show invoice

# 匯出Schema到檔案
docextract schema --show invoice --export invoice_schema.json
```

#### 自訂Schema

建立JSON Schema檔案定義您的提取欄位：

```json
{
  "name": "CustomInvoice",
  "description": "我的自訂發票Schema",
  "fields": [
    {"name": "invoice_id", "type": "string", "required": true},
    {"name": "amount", "type": "currency", "required": true},
    {"name": "date", "type": "date", "required": true}
  ]
}
```

使用它：
```bash
docextract extract doc.pdf --provider openai --api-key $KEY --schema-file my_schema.json
```

#### 支援的欄位類型

| 類型 | 描述 | 範例 |
|------|------|---------|
| `string` | 文字值 | `"Hello"` |
| `integer` | 整數 | `42` |
| `float` | 小數 | `3.14` |
| `boolean` | 布林值 | `true` |
| `date` | 日期字串 | `"2024-01-15"` |
| `email` | 電子郵件 | `"user@example.com"` |
| `url` | 網址 | `"https://example.com"` |
| `phone` | 電話號碼 | `"+1-234-567-8900"` |
| `currency` | 貨幣值 | `"$1,234.56"` |
| `list` | 陣列 | `["a", "b"]` |
| `object` | 巢狀物件 | `{"name": "John"}` |

#### 查看歷史與統計

```bash
# 查看最近提取記錄
docextract history --limit 20

# 查看統計資訊
docextract stats

# 匯出歷史到CSV
docextract history --export results.csv
```

### 💡 設計理念

**單一用途，做到極致**

與PaddleOCR（80K⭐，重依賴）或open-notebook（25K⭐，全端應用）等大型框架不同，DocExtract-AI-CLI專注於一個任務：**結構化資料提取**。這使其：

- **輕量級**：零外部依賴
- **快速**：最小開銷，直接處理
- **可攜帶**：任何能執行Python的地方都能工作
- **可組合**：易於整合到流水線中

**Schema優先方法**

無需訓練自訂模型或編寫複雜解析器，您只需在Schema中描述所需內容。AI負責理解文件並提取正確資訊。

### 📦 開發

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
make test

# 執行測試（含覆蓋率）
make test-cov

# 格式化程式碼
make format

# 執行程式碼檢查
make lint

# 清理建構產物
make clean
```

### 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 倉庫
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立 Pull Request

### 📄 開源授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

---

<div align="center">

**Made with 🦞 by gitstq**

[⭐ Star this repo](https://github.com/gitstq/DocExtract-AI-CLI) if you find it useful!

</div>
