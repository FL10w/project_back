from pydantic import BaseModel
from typing import Optional

class ContentSummaryRequest(BaseModel):
    title: str
    content_type: str
    author: Optional[str] = None
    year: Optional[str] = None

class ContentSummaryResponse(BaseModel):
    title: str
    content_type: str
    summary: str
    author: Optional[str] = None
    year: Optional[str] = None