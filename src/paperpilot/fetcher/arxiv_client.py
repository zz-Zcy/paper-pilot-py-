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
        self.client = arxiv.Client()
        self.max_results = max_results
    
    def search(self, query: str, sort_by: str = "submittedDate") -> List[PaperMetadata]:
        search = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=getattr(arxiv.SortCriterion, sort_by, arxiv.SortCriterion.SubmittedDate)
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
            comment=result.comment
        )