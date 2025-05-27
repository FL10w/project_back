import requests
from fastapi import HTTPException
from typing import List, Dict, Optional, Union
from urllib.parse import urljoin
import os
from dotenv import load_dotenv
from enum import Enum
import logging

load_dotenv()


KINOPOISK_API_BASE = "https://kinopoiskapiunofficial.tech/api/v2.2/"
KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY")


logger = logging.getLogger(__name__)

class TopFilmType(str, Enum):
    TOP_250_BEST_FILMS = "TOP_250_BEST_FILMS"
    TOP_100_POPULAR_FILMS = "TOP_100_POPULAR_FILMS"
    TOP_AWAIT_FILMS = "TOP_AWAIT_FILMS"
    TOP_250_TV_SHOWS = "TOP_250_TV_SHOWS"
    TOP_POPULAR_ALL = "TOP_POPULAR_ALL"
    TOP_POPULAR_MOVIES = "TOP_POPULAR_MOVIES"
    VAMPIRE_THEME = "VAMPIRE_THEME"
    COMICS_THEME = "COMICS_THEME"
    CLOSES_RELEASES = "CLOSES_RELEASES"
    FAMILY = "FAMILY"
    OSKAR_WINNERS_2021 = "OSKAR_WINNERS_2021"
    LOVE_THEME = "LOVE_THEME"
    ZOMBIE_THEME = "ZOMBIE_THEME"

class KinopoiskAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": KINOPOISK_API_KEY,
            "Content-Type": "application/json",
        })

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Union[Dict, List]:
        """Базовый метод для выполнения запросов"""
        url = urljoin(KINOPOISK_API_BASE, endpoint)
        logger.info(f"Making request to {url} with params {params}")
        try:
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            logger.info(f"Request to {endpoint} successful")
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {endpoint}: {str(e)}")
            status_code = e.response.status_code
            try:
                detail = e.response.json().get("message", str(e))
            except ValueError:
                detail = str(e)
            raise HTTPException(
                status_code=status_code,
                detail=f"Kinopoisk API error: {detail}"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {endpoint}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Kinopoisk API error: {str(e)}"
            )

    async def search_films(self, query: str, page: int = 1) -> List[Dict]:
        """Поиск фильмов и сериалов"""
        data = await self._make_request("films", {"keyword": query, "page": page})
        return [self._process_film_item(item) for item in data.get("items", [])]

    async def get_film_details(self, film_id: int) -> Dict:
        """Получение полной информации о фильме/сериале"""
        data = await self._make_request(f"films/{film_id}")
        return self._process_film_item(data, detailed=True)

    async def get_film_sequels_and_prequels(self, film_id: int) -> List[Dict]:
        """Получение сиквелов и приквелов"""
        data = await self._make_request(f"films/{film_id}/sequels_and_prequels")
        return [self._process_film_item(item) for item in data]

    async def get_collection(
            self,
            collection_type: TopFilmType,
            page: int = 1,
            limit: int = 20
    ) -> List[Dict]:
        """
        Универсальный метод для получения любых подборок
        Args:
            collection_type: Тип подборки из TopFilmType
            page: Номер страницы (начинается с 1)
            limit: Количество элементов на странице (макс. 20)
        """
        top_types = [
            TopFilmType.TOP_250_BEST_FILMS,
            TopFilmType.TOP_100_POPULAR_FILMS,
            TopFilmType.TOP_AWAIT_FILMS,
            TopFilmType.LOVE_THEME
        ]

        if collection_type in top_types:
            params = {
                "type": collection_type.value,
                "page": page
            }
            endpoint = "films/collections" if collection_type == TopFilmType.LOVE_THEME else "films/top"
            data = await self._make_request(endpoint, params)
            items = [self._process_film_item(item) for item in data.get("items", data.get("films", []))]
            return items[:min(limit, len(items))]
        elif collection_type == TopFilmType.TOP_250_TV_SHOWS:
            params = {
                "type": "TV_SERIES",
                "order": "RATING",
                "page": page,
                "limit": min(limit, 20)
            }
            data = await self._make_request("films", params)
            items = [self._process_film_item(item) for item in data.get("items", [])]
            return items
        else:
            return await self.get_thematic_collection(collection_type, page, limit)

    async def get_thematic_collection(
            self,
            collection_type: TopFilmType,
            page: int = 1,
            limit: int = 20
    ) -> List[Dict]:
        """
        Получение тематических подборок через фильтры
        Args:
            collection_type: Тип подборки из TopFilmType
            page: Номер страницы
            limit: Количество элементов на странице (макс. 20)
        """
        theme_filters = {
            TopFilmType.FAMILY: {"genres": "19"},
            TopFilmType.VAMPIRE_THEME: {"keyword": "вампиры"},
            TopFilmType.ZOMBIE_THEME: {"keyword": "зомби"},
            TopFilmType.COMICS_THEME: {"keyword": "комиксы"},
            TopFilmType.OSKAR_WINNERS_2021: {"keyword": "оскар 2021"},
            TopFilmType.CLOSES_RELEASES: {"order": "YEAR", "yearFrom": 2023},
            TopFilmType.TOP_POPULAR_ALL: {"order": "RATING"},
            TopFilmType.TOP_POPULAR_MOVIES: {"order": "RATING", "type": "FILM"}
        }

        params = {
            "page": page,
            "limit": min(limit, 20)
        }
        if collection_type in theme_filters:
            params.update(theme_filters[collection_type])
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported collection type: {collection_type.value}"
            )

        data = await self._make_request("films", params)
        return [self._process_film_item(item) for item in data.get("items", [])]

    def _process_film_item(self, item: Dict, detailed: bool = False) -> Dict:
        """Обработка данных о фильме/сериале"""
        result = {
            "kp_id": item.get("kinopoiskId") or item.get("filmId"),
            "imdb_id": item.get("imdbId"),
            "title_ru": item.get("nameRu"),
            "title_en": item.get("nameEn"),
            "title_original": item.get("nameOriginal"),
            "poster_url": item.get("posterUrl"),
            "poster_url_preview": item.get("posterUrlPreview"),
            "year": item.get("year"),
            "film_length": item.get("filmLength"),
            "slogan": item.get("slogan"),
            "description": item.get("description"),
            "short_description": item.get("shortDescription"),
            "rating_kinopoisk": item.get("ratingKinopoisk"),
            "rating_imdb": item.get("ratingImdb"),
            "rating_age_limits": item.get("ratingAgeLimits"),
            "type": item.get("type"),
            "is_series": item.get("serial") or (item.get("type") == "TV_SERIES"),
            "start_year": item.get("startYear"),
            "end_year": item.get("endYear"),
        }

        if detailed:
            result.update({
                "countries": [c["country"] for c in item.get("countries", [])],
                "genres": [g["genre"] for g in item.get("genres", [])],
                "facts": [f["text"] for f in item.get("facts", [])],
                "distributors": item.get("distributors"),
                "premiere_world": item.get("premiereWorld"),
                "premiere_russia": item.get("premiereRussia"),
                "premiere_digital": item.get("premiereDigital"),
            })

        if detailed and item.get("posters"):
            posters = item["posters"]
            result.update({
                "posters": {
                    "vertical": [p["url"] for p in posters if p.get("type") == "vertical"],
                    "horizontal": [p["url"] for p in posters if p.get("type") == "horizontal"],
                }
            })

        if result["is_series"] and item.get("seasons"):
            seasons = []
            for season in item["seasons"]:
                seasons.append({
                    "number": season.get("number"),
                    "episodes": season.get("episodes"),
                    "year": season.get("year"),
                })
            result["seasons_info"] = seasons

        return result