import os
import sys

import typer
from rich.console import Console
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from paperpilot.fetcher.arxiv_client import ArxivClient, download_pdf
from paperpilot.parser.pdf_extractor import PDFExtractor
from paperpilot.summarizer.factory import LLMFactory
from paperpilot.summarizer.prompts import PAPER_SUMMARY_TEMPLATE

app = typer.Typer()
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="搜索关键词"),
    max_results: int = typer.Option(10, "--max", "-n", help="最大结果数"),
):
    """搜索 arXiv 论文"""
    console.print(f"🔍 正在搜索: [bold cyan]{query}[/bold cyan]")
    
    client = ArxivClient(max_results=max_results)
    papers = client.search(query)
    
    table = Table(title=f"找到 {len(papers)} 篇论文")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("标题", style="green")
    table.add_column("第一作者", style="yellow")
    table.add_column("日期", style="magenta")
    
    for p in papers:
        authors = ", ".join(p.authors[:2]) + ("..." if len(p.authors) > 2 else "")
        table.add_row(p.arxiv_id, p.title[:60], authors, p.published.strftime("%Y-%m-%d"))
    
    console.print(table)


@app.command()
def summarize(
    arxiv_id: str = typer.Argument(..., help="论文 arXiv ID"),
    output: str = typer.Option(None, "--output", "-o", help="输出文件路径"),
    provider: str = typer.Option(None, "--provider", "-p", help="LLM 提供商"),
):
    """下载并总结单篇论文"""
    console.print(f"📄 正在获取论文 {arxiv_id}...")
    
    # 1. 搜索论文元数据
    client = ArxivClient()
    papers = client.search(f"id:{arxiv_id}", max_results=1)
    if not papers:
        console.print("[red]❌ 论文未找到[/red]")
        raise typer.Exit(1)
    
    paper = papers[0]
    console.print(f"✅ 找到: {paper.title}")
    
    # 2. 下载 PDF
    console.print("⬇️  下载 PDF...")
    pdf_path = download_pdf(paper)
    console.print(f"💾 已下载: {pdf_path}")
    
    # 3. 解析内容
    console.print("📖 解析内容...")
    extractor = PDFExtractor(pdf_path)
    content = extractor.extract_text(max_pages=10)
    
    # 4. 生成总结
    console.print("🤖 正在生成总结...")
    llm = LLMFactory.create(provider)
    
    prompt = PAPER_SUMMARY_TEMPLATE.format(
        title=paper.title,
        authors=", ".join(paper.authors),
        abstract=paper.abstract,
        content=content[:8000]  # 限制长度
    )
    
    summary = llm.summarize(prompt, stream=False)
    
    # 5. 输出
    console.print("\n" + "="*50)
    console.print(summary)
    console.print("="*50)
    
    # 6. 保存文件
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(f"# {paper.title}\n\n")
            f.write(f"**作者**: {', '.join(paper.authors)}\n\n")
            f.write(f"**arXiv ID**: {paper.arxiv_id}\n\n")
            f.write(f"**PDF**: {paper.pdf_url}\n\n")
            f.write("---\n\n")
            f.write(summary)
        console.print(f"\n💾 已保存到: {output}")


@app.command()
def test_llm(
    provider: str = typer.Option(None, "--provider", "-p", help="LLM 提供商"),
    message: str = typer.Option("请介绍你自己", "--message", "-m", help="测试消息"),
    stream: bool = typer.Option(False, "--stream", help="流式输出"),
):
    """测试 LLM 连接"""
    try:
        client = LLMFactory.create(provider)
        console.print(f"✅ 使用模型: [bold green]{client.name}[/bold green]\n")
        
        prompt = f"请用一句话回答：{message}"
        
        if stream:
            console.print("🤖 ", end="")
            for chunk in client.summarize(prompt, stream=True):
                console.print(chunk, end="")
            console.print("\n")
        else:
            result = client.summarize(prompt, stream=False)
            console.print(f"🤖 {result}\n")
            
    except Exception as e:
        console.print(f"[bold red]❌ 错误: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def list_providers():
    """列出支持的 LLM 提供商"""
    providers = LLMFactory.list_providers()
    console.print("[bold]支持的提供商:[/bold]")
    for p in providers:
        marker = "✓" if p == os.getenv("LLM_PROVIDER", "ollama") else " "
        console.print(f"  [{marker}] {p}")


if __name__ == "__main__":
    app()