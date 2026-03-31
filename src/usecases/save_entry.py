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


class SaveEntryUseCase:
    """Сценарий: пользователь отправляет текст → сохраняем → анализируем."""

    def __init__(
        self,
        repository: EntrySaver,
        analyzer: Analyzer | None = None,
    ) -> None:
        self.repository = repository
        self.analyzer = analyzer

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

        return entry
