import arxiv
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PaperMetadata:
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published: datetime
    primary_category: str
    categories: List[str]
    pdf_url: str
    comment: Optional[str] = None


class ArxivClient:
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.client = arxiv.Client()

    def search(self, query: str, sort_by: str = "submittedDate", max_results: int = None) -> List[PaperMetadata]:
        if max_results is None:
            max_results = self.max_results

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=getattr(arxiv.SortCriterion, sort_by, arxiv.SortCriterion.SubmittedDate),
        )
        return [self._to_metadata(result) for result in self.client.results(search)]

    def _to_metadata(self, result: arxiv.Result) -> PaperMetadata:
        return PaperMetadata(
            arxiv_id=result.get_short_id(),
            title=result.title,
            authors=[str(a) for a in result.authors],
            abstract=result.summary,
            published=result.published,
            primary_category=result.primary_category,
            categories=result.categories,
            pdf_url=result.pdf_url,
            comment=result.comment,
        )


import os
import requests
from pathlib import Path


def download_pdf(paper: PaperMetadata, output_dir: str = "./papers") -> str:
    """下载论文 PDF"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{paper.arxiv_id}.pdf")

    if os.path.exists(filepath):
        return filepath

    response = requests.get(paper.pdf_url, timeout=60)
    response.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(response.content)

    return filepath