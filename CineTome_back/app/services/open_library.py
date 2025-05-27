import httpx
from fastapi import HTTPException
from typing import Optional, List


async def search_books(
        query: str,
        limit: int = 5,
        page: int = 1,
        search_type: Optional[str] = None,
        sort_by_popularity: bool = False,
        sort_by_new: bool = False,
        translate: bool = True
):
    url = "https://openlibrary.org/search.json"
    params = {
        "limit": limit,
        "page": page,
        "fields": "title,author_name,first_publish_year,cover_i,key,isbn,description,subjects,edition_count"
    }

    if sort_by_new:
        params["sort"] = "new"

    if search_type == "author":
        params["author"] = query
    elif search_type == "isbn":
        params["q"] = f"isbn:{query}"
    elif search_type == "subject":
        params["q"] = f"subject:{query}"
    else:
        params["q"] = query

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            books = [{
                "title": book.get("title", "Без названия"),
                "authors": book.get("author_name", []),
                "year": book.get("first_publish_year"),
                "cover_url": f"https://covers.openlibrary.org/b/id/{book['cover_i']}-L.jpg" if book.get(
                    "cover_i") else None,
                "work_id": book["key"].split("/")[-1] if book.get("key") and "/works/" in book["key"] else None,
                "description": book.get("description", "Описание отсутствует") if isinstance(book.get("description"),
                                                                                             str) else "Описание отсутствует",
                "subjects": book.get("subjects", []),
                "edition_count": book.get("edition_count", 0),
                "rating": 0.0
            } for book in data.get("docs", []) if book.get("key") and "/works/" in book["key"]]

            if sort_by_popularity:
                books.sort(key=lambda x: x["edition_count"], reverse=True)

            return books
        except httpx.HTTPStatusError as e:
            print(f"OpenLibrary HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка API OpenLibrary: {str(e)}")
        except Exception as e:
            print(f"OpenLibrary general error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


async def get_book_details(work_id: str, translate: bool = True):
    url = f"https://openlibrary.org/works/{work_id}.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            authors = [
                author.get("name") for author in data.get("authors", [])
                if isinstance(author.get("name"), str)
            ]

            book = {
                "title": data.get("title", "Название не указано"),
                "authors": authors,
                "publish_year": data.get("first_publish_year"),
                "description": data.get("description", "Описание отсутствует") if isinstance(data.get("description"),
                                                                                             str) else "Описание отсутствует",
                "cover_url": f"https://covers.openlibrary.org/b/id/{data.get('covers', [None])[0]}-L.jpg" if data.get(
                    "covers") and data.get("covers")[0] else None,
                "openlibrary_url": f"https://openlibrary.org/works/{work_id}"
            }

            return book
        except httpx.HTTPStatusError as e:
            print(f"OpenLibrary HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Книга не найдена: {str(e)}")
        except Exception as e:
            print(f"OpenLibrary general error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")