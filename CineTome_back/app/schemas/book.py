from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class BookSearchResult(BaseModel):
    title: str
    authors: List[str]
    year: Optional[int] = None
    cover_url: Optional[HttpUrl] = None
    work_id: str

class BookDetails(BaseModel):
    title: str
    authors: List[str]
    publish_year: Optional[int] = None
    description: str
    cover_url: Optional[HttpUrl] = None
    openlibrary_url: HttpUrl