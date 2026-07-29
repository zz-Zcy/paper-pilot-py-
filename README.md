# PaperPilot

&gt; 基于 LLM 的 arXiv 论文自动化总结工具，一键完成搜索-下载-解析-总结全流程。

## 功能特性

- 🔍 **arXiv 搜索** — 支持关键词搜索，快速获取论文元数据
- ⬇️ **自动下载** — 自动下载 PDF 并本地缓存
- 📄 **PDF 解析** — 提取前10页核心内容
- 🤖 **AI 总结** — 调用 DeepSeek/OpenAI API 生成结构化摘要
- 📝 **Markdown 输出** — 统一格式，可接入 Obsidian/Zotero 等知识库
- 🔄 **多模型切换** — 工厂模式设计，支持灵活扩展

## 快速开始

### 1. 安装

```bash
git clone https://github.com/zz-Zcy/paper-pilot-py-.git
cd paper-pilot-py-
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate

pip install -e .
```
### 2. 配置 API Key

- 复制 `env.example` 到根目录，重命名为 `.env`
- 填入你的 DeepSeek 或 OpenAI API Key, 根据 `env.example` 里面的提示补充和选择对应的模型
- 保存文件

### 3. 运行

- 搜索论文：
```bash
python -m paperpilot.cli.main search "transformer architecture" --max 5
```
- 总结单篇 论文：
```bash
python -m paperpilot.cli.main summarize 1706.03762 --output summary.md
```
- 1706.03762 是 arXiv ID，可以在论文 URL 中找到。

- 测试 LLM 连接：
```bash
python -m paperpilot.cli.main test-llm
```
- 列出支持的模型提供商：
```bash
python -m paperpilot.cli.main list-providers
```

- 项目结构
```
   plain text
paper-pilot-py-/
├── src/paperpilot/
│   ├── cli/              # 命令行接口
│   │   └── main.py       # Typer CLI 入口
│   ├── fetcher/          # 论文获取
│   │   └── arxiv_client.py   # arXiv API 封装 + PDF 下载
│   ├── parser/           # 内容解析
│   │   └── pdf_extractor.py  # PDF 文本提取
│   ├── summarizer/       # LLM 总结
│   │   ├── base.py       # 抽象基类
│   │   ├── factory.py    # 工厂模式，自动创建客户端
│   │   ├── api_client.py # DeepSeek / OpenAI 客户端
│   │   ├── ollama_client.py  # Ollama 本地模型客户端（预留）
│   │   └── prompts.py    # 结构化总结提示词模板
│   └── config/           # 配置管理
├── .env.example          # 环境变量模板
├── pyproject.toml        # 项目配置
└── README.md             # 本文件
```

- 技术栈：
```plain text
Python 3.9+
Typer — 命令行框架
Rich — 终端美化
arxiv — arXiv 官方 API
pdfplumber — PDF 文本提取
Pydantic — 数据校验
requests — HTTP 客户端
```

- 输出示例：
```markdown
# Attention Is All You Need

**作者**: Ashish Vaswani, Noam Shazeer, Niki Parmar, et al.

**arXiv ID**: 1706.03762

**PDF**: https://arxiv.org/pdf/1706.03762.pdf

---

## 核心贡献
提出了 Transformer 架构，完全基于注意力机制，摒弃了 RNN 和 CNN...

## 方法概述
使用多头自注意力机制 (Multi-Head Self-Attention) 和位置编码...

## 关键结果
在 WMT 2014 英德翻译任务上达到 BLEU 28.4，训练时间大幅减少...

## 局限性与未来工作
...
```

# 开发：
- 安装开发依赖
```bash
pip install -e ".[dev]"
```

- 代码格式化
black src tests
ruff check src tests

## 开发计划：
- [ ] 目前只能通过接大模型api使用，后续会考虑增加本地模型支持
- [ ] 完善错误处理机制