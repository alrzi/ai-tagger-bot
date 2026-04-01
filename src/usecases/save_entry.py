"""Use case: сохранение записи пользователя."""

from __future__ import annotations

import logging
from typing import Protocol

from src.domain.entities import ContentType, Entry

logger = logging.getLogger(__name__)


class EntrySaver(Protocol):
    """Протокол для сохранения записи."""

    async def save(self, entry: Entry) -> Entry: ...


class Analyzer(Protocol):
    """Протокол для анализа записи."""

    async def execute(self, entry_id: int, user_id: int) -> Entry: ...


class Embedder(Protocol):
    """Протокол для генерации эмбеддинга."""

    async def embed(self, text: str) -> list[float]: ...


class EmbeddingUpdater(Protocol):
    """Протокол для обновления эмбеддинга в БД."""

    async def update_embedding(self, entry_id: int, embedding: list[float]) -> None: ...


class SaveEntryUseCase:
    """Сценарий: пользователь отправляет текст → сохраняем → анализируем."""

    def __init__(
        self,
        repository: EntrySaver,
        analyzer: Analyzer | None = None,
        embedder: Embedder | None = None,
        embedding_updater: EmbeddingUpdater | None = None,
    ) -> None:
        self.repository = repository
        self.analyzer = analyzer
        self.embedder = embedder
        self.embedding_updater = embedding_updater

    async def execute(
        self,
        user_id: int,
        text: str | None = None,
        url: str | None = None,
    ) -> Entry:
        raw_text = text or ""
        if url:
            raw_text = raw_text or url

        if not raw_text.strip():
            raise ValueError("Нет контента для сохранения")

        entry = Entry(
            user_id=user_id,
            url=url,
            raw_text=raw_text,
            content_type=ContentType.UNKNOWN,
        )

        entry = await self.repository.save(entry)

        # Анализ через ИИ (если доступен)
        if self.analyzer and entry.id:
            try:
                entry = await self.analyzer.execute(entry.id, user_id)
            except Exception as e:
                logger.warning("Ошибка анализа записи %s: %s", entry.id, e)

        # Генерация эмбеддинга (если доступен)
        if self.embedder and self.embedding_updater and entry.id:
            try:
                text_for_embedding = entry.summary or entry.raw_text
                embedding = await self.embedder.embed(text_for_embedding[:2000])
                await self.embedding_updater.update_embedding(entry.id, embedding)
                entry.embedding = embedding
            except Exception as e:
                logger.warning("Ошибка генерации эмбеддинга для записи %s: %s", entry.id, e)

        return entry
