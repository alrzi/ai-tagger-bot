"""Сервис для генерации векторных эмбеддингов."""

from __future__ import annotations

from typing import Protocol

import httpx

from config.settings import settings


class EmbeddingGenerator(Protocol):
    """Протокол для генерации эмбеддингов."""

    async def embed(self, text: str) -> list[float]: ...


class OllamaEmbeddingService:
    """Генерация эмбеддингов через Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def embed(self, text: str) -> list[float]:
        """Генерирует векторный эмбеддинг для текста."""
        async with httpx.AsyncClient() as client:
            # Пробуем новый endpoint /api/embed (Ollama 0.1.26+)
            try:
                resp = await client.post(
                    f"{self.base_url}/api/embed",
                    json={"model": self.model, "input": text[:2000]},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                # /api/embed возвращает {"embeddings": [[...]]}
                return data["embeddings"][0]
            except (KeyError, IndexError):
                # Fallback на старый endpoint /api/embeddings
                resp = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text[:2000]},
                    timeout=60,
                )
                resp.raise_for_status()
                return resp.json()["embedding"]
