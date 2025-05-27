from fastapi import APIRouter, HTTPException
from app.services.gigachat_client import get_gigachat_client
from app.schemas.ai import ContentSummaryRequest, ContentSummaryResponse
from pydantic import BaseModel
from typing import Optional
import logging
router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger(__name__)

class SummaryRequest(BaseModel):
    title: str
    content_type: str
    author: Optional[str] = None
    year: Optional[str] = None

@router.post("/generate-summary")
async def generate_summary(request: SummaryRequest):
    """Генерация краткого описания для любого типа контента"""
    try:
        gigachat = get_gigachat_client()
        summary = gigachat.generate_content_summary(
            title=request.title,
            content_type=request.content_type,
            author=request.author,
            year=request.year
        )
        return {"summary": summary}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"AI summary generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate content summary"
        )
@router.post("/generate-summary", response_model=ContentSummaryResponse)
async def generate_content_summary(request: ContentSummaryRequest):
    try:
        client = get_gigachat_client()
        summary = client.generate_content_summary(
            title=request.title,
            content_type=request.content_type,
            author=request.author,
            year=request.year
        )

        return ContentSummaryResponse(
            title=request.title,
            content_type=request.content_type,
            summary=summary,
            author=request.author,
            year=request.year
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при генерации описания: {str(e)}"
        )