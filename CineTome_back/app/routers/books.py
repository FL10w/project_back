from fastapi import APIRouter, Query, HTTPException, Path
from typing import List, Optional
from app.services.open_library import search_books, get_book_details
from app.schemas.book import BookSearchResult, BookDetails
from app.services.gigachat_client import get_gigachat_client
import logging

router = APIRouter(prefix="/books", tags=["Books"])
logger = logging.getLogger(__name__)


@router.get("/search/", response_model=List[BookSearchResult])
async def book_search(
    query: str = Query(..., min_length=2, example="Harry Potter", description="Поисковый запрос (название, автор, жанр и т.д.)"),
    limit: int = Query(5, ge=1, le=100, description="Количество книг на странице (1-100)"),
    page: int = Query(1, ge=1, description="Номер страницы для пагинации"),
    search_type: Optional[str] = Query(None, description="Тип поиска: 'author' (по автору), 'isbn' (по ISBN), 'subject' (по жанру), None (общий поиск)"),
    sort_by_popularity: bool = Query(False, description="Сортировать по популярности (по количеству изданий)"),
    sort_by_new: bool = Query(False, description="Сортировать по новизне (от новых к старым)"),
    translate: bool = Query(False, description="Перевести данные на русский язык")
):
    """
    Поиск книг по названию, автору, ISBN или жанру через OpenLibrary.
    Возвращает список книг с work_id для получения деталей.
    """
    return await search_books(query, limit, page, search_type, sort_by_popularity, sort_by_new, translate)


@router.get("/{work_id}")
async def book_details(
        work_id: str = Path(..., regex=r"^OL\d+W$"),
        translate: bool = Query(False),
        with_summary: bool = Query(False, description="Генерировать краткое описание с помощью AI")
):
    """Получение деталей книги с опциональным AI-описанием"""
    try:
        book = await get_book_details(work_id, translate)

        if with_summary:
            try:
                gigachat = get_gigachat_client()
                book["summary"] = gigachat.generate_content_summary(
                    title=book.get("title"),
                    content_type="book",
                    author=", ".join(book.get("authors", [])),
                    year=str(book.get("publish_year", ""))
                )
            except Exception as e:
                logger.error(f"Failed to generate book summary: {str(e)}")
                book["summary"] = None

        return book
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=404, detail="Book not found")