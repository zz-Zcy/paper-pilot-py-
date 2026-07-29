import pdfplumber
from pathlib import Path


class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
    
    def extract_text(self, max_pages: int = 10) -> str:
        """提取 PDF 文本，默认只读前10页（摘要+引言+方法）"""
        text_parts = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= max_pages:
                    break
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts)