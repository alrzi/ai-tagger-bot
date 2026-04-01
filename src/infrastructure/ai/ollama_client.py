"""Клиент для Ollama API."""

from __future__ import annotations

from typing import Any, TypeVar, cast

import httpx
from pydantic import BaseModel

from config.settings import settings

T = TypeVar("T", bound=BaseModel)


class OllamaClient:
    """Async клиент к Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def health_check(self) -> bool:
        """Проверяет, доступен ли Ollama."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{self.base_url}/api/tags", timeout=10)
                resp.raise_for_status()
                return True
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """Возвращает список доступных моделей."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/tags", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]

    async def generate(self, prompt: str, system: str | None = None) -> str:
        """Отправляет промпт и получает текстовый ответ."""
        payload: dict[str, Any] = {  # type: ignore[misc]
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return cast(str, resp.json()["response"])

    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system: str | None = None,
    ) -> T:
        """Отправляет промпт с JSON Schema, возвращает распарсенную DTO.

        Ollama получает схему через параметр format и гарантирует
        валидный JSON нужной структуры.
        """
        payload: dict[str, Any] = {  # type: ignore[misc]
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": schema.model_json_schema(),
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return schema.model_validate_json(resp.json()["response"])

    async def embed(self, text: str) -> list[float]:
        """Получает векторный эмбеддинг текста."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text[:2000]},
                timeout=60,
            )
            resp.raise_for_status()
            return cast(list[float], resp.json()["embedding"])
