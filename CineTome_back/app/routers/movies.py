from fastapi import APIRouter, Query, HTTPException, Path
from app.services.kinopoisk_client import KinopoiskAPI, TopFilmType
from app.services.gigachat_client import get_gigachat_client
from typing import Optional, Dict
import logging

router = APIRouter(prefix="/api/kp", tags=["Kinopoisk"])
logger = logging.getLogger(__name__)
kp_api = KinopoiskAPI()


TOP_TYPES = {
    "best": "TOP_250_BEST_FILMS",
    "popular": "TOP_100_POPULAR_FILMS",
    "await": "TOP_AWAIT_FILMS",
    "series": "TOP_250_TV_SHOWS",
}

@router.get("/search")
async def search_content(
    query: str = Query(..., min_length=2, example="Пираты"),
    page: int = Query(1, ge=1),
    content_type: str = Query("ALL", regex="^(FILM|TV_SERIES|TV_SHOW|MINI_SERIES|ALL)$")
):
    """
    Поиск фильмов и сериалов по названию
    - query: строка поиска
    - page: номер страницы
    - content_type: тип контента (FILM, TV_SERIES, TV_SHOW, MINI_SERIES, ALL)
    """
    return await kp_api.search_films(query, page)

@router.get("/collections")
async def get_collection(
    type: TopFilmType = Query(
        TopFilmType.TOP_250_BEST_FILMS,
        description="Тип подборки. Доступные значения: " +
        ", ".join([f"{t.value} ({t.name})" for t in TopFilmType])
    ),
    page: int = Query(1, ge=1, description="Номер страницы")
):
    """
    Получение фильмов из различных подборок Кинопоиска.
    Поддерживает все типы топов и тематических подборок.
    """
    return await kp_api.get_collection(
        collection_type=type,
        page=page
    )
@router.get("/films/{film_id}")
async def get_film_details(
    film_id: int = Path(..., description="Kinopoisk ID фильма"),
    with_sequels: bool = Query(False, description="Включить информацию о сиквелах и приквелах"),
    with_similars: bool = Query(False, description="Включить похожие фильмы"),
    with_reviews: bool = Query(False, description="Включить рецензии"),
    with_videos: bool = Query(False, description="Включить видеоматериалы"),
    with_summary: bool = Query(False, description="Генерировать краткое описание с помощью AI")
):
    """Полная информация о фильме/сериале"""
    film = await kp_api.get_film_details(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")

    # Дополнительные данные
    if with_sequels:
        film["sequels_and_prequels"] = await kp_api.get_film_sequels_and_prequels(film_id)
    if with_similars:
        film["similars"] = await kp_api.get_film_similars(film_id)
    if with_reviews:
        film["reviews"] = await kp_api.get_film_reviews(film_id)
    if with_videos:
        film["videos"] = await kp_api.get_film_videos(film_id)

    # AI-описание
    if with_summary:
        try:
            gigachat = get_gigachat_client()
            film["ai_summary"] = gigachat.generate_content_summary(
                title=film.get("title_ru") or film.get("title_en"),
                content_type="series" if film.get("is_series") else "movie",
                year=film.get("year")
            )
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            film["ai_summary"] = None

    return film

@router.get("/series/{series_id}")
async def get_series_details(
    series_id: int = Path(..., description="Kinopoisk ID сериала"),
    with_seasons: bool = Query(True, description="Включить информацию о сезонах"),
    with_summary: bool = Query(False, description="Генерировать краткое описание с помощью AI")
):
    """Информация о сериале (специализированный endpoint)"""
    series = await kp_api.get_film_details(series_id)
    if not series or not series.get("is_series"):
        raise HTTPException(status_code=404, detail="Series not found")

    if not with_seasons and "seasons_info" in series:
        del series["seasons_info"]

    if with_summary:
        try:
            gigachat = get_gigachat_client()
            series["ai_summary"] = gigachat.generate_content_summary(
                title=series.get("title_ru") or series.get("title_en"),
                content_type="series",
                year=series.get("year"),
                seasons=series.get("seasons_info")
            )
        except Exception as e:
            logger.error(f"Failed to generate series summary: {str(e)}")
            series["ai_summary"] = None

    return series