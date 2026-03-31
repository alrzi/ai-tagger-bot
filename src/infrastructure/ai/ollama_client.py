"""Клиент для Ollama API."""

from __future__ import annotations

import json
from typing import Any

import httpx

from config.settings import settings


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
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
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
            return resp.json()["response"]

    async def embed(self, text: str) -> list[float]:
        """Получает векторный эмбеддинг текста."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text[:2000]},
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]
