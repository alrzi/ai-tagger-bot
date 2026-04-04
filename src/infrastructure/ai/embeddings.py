"""Сервис для генерации векторных эмбеддингов."""

from __future__ import annotations

from typing import cast

import httpx

from config.settings import Settings


class NomicEmbeddingService:
    """Генерация эмбеддингов через локальный Ollama."""

    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.ollama_url.rstrip("/")
        self.model = settings.ollama_embedding_model

    async def embed(self, text: str) -> list[float]:
        """Генерирует векторный эмбеддинг для текста."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text[:8000],
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return cast(list[float], data["embedding"])

