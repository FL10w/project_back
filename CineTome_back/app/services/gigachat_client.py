import os
import base64
from gigachat import GigaChat
from fastapi import HTTPException
from typing import Optional
import httpx
import json
import ssl
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class GigaChatClient:
    def __init__(self):
        self.ssl_context = ssl._create_unverified_context()
        self._access_token = None
        self._token_expires = None
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Инициализация клиента с актуальным токеном"""
        self.access_token = self._get_access_token()
        self.client = GigaChat(
            access_token=self.access_token,
            verify_ssl_certs=False,
            ssl_context=self.ssl_context
        )

    @property
    def access_token(self):
        """Получение токена с проверкой срока действия"""
        if self._access_token is None or self._is_token_expired():
            self._access_token = self._get_access_token()
            self._token_expires = datetime.now() + timedelta(minutes=30)
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        self._access_token = value

    def _is_token_expired(self):
        """Проверка истечения срока действия токена"""
        return self._token_expires is None or datetime.now() >= self._token_expires

    def _get_access_token(self) -> str:
        """Получение access token с отключенной SSL проверкой"""
        if os.getenv("GIGACHAT_AUTH_KEY") is None:
            raise HTTPException(
                status_code=500,
                detail="GigaChat credentials not configured"
            )

        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        scope = os.getenv("GIGACHAT_SCOPE")
        auth_url = os.getenv("GIGACHAT_AUTH_URL")

        headers = {
            "Authorization": f"Bearer {auth_key}",
            "RqUID": client_id,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"scope": scope}

        try:
            transport = httpx.HTTPTransport(retries=3, verify=False)
            with httpx.Client(transport=transport) as client:
                response = client.post(
                    auth_url,
                    headers=headers,
                    data=data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["access_token"]
        except Exception as e:
            logger.error(f"GigaChat auth failed: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="GigaChat authentication service unavailable"
            )

    def generate_content_summary(self, title: str, content_type: str,
                                 author: Optional[str] = None,
                                 year: Optional[str] = None) -> str:
        """Генерация краткого содержания для фильма/сериала/книги"""
        prompt = self._build_summary_prompt(title, content_type, author, year)

        try:
            response = self.client.chat(prompt)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GigaChat API error: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="GigaChat service temporarily unavailable"
            )

    def _build_summary_prompt(self, title: str, content_type: str,
                              author: Optional[str], year: Optional[str]) -> str:
        """Формирование промпта для генерации описания"""
        content_type_name = self._get_content_type_name(content_type)
        prompt_parts = [
            f"Сгенерируй краткое содержание {content_type_name} '{title}'"
        ]

        if author:
            prompt_parts.append(f" автора {author}")
        if year:
            prompt_parts.append(f" ({year} года)")

        prompt_parts.append(
            ". Ограничься 3-5 предложениями. Описывай основной сюжет, но без спойлеров ключевых моментов.")

        return "".join(prompt_parts)

    def _get_content_type_name(self, content_type: str) -> str:
        """Возвращает читаемое название типа контента"""
        return {
            "movie": "фильма",
            "series": "сериала",
            "book": "книги"
        }.get(content_type, "контента")


def get_gigachat_client() -> GigaChatClient:
    """Фабрика для получения клиента GigaChat с ленивой инициализацией"""
    return GigaChatClient()