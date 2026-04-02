"""Use case: сохранение записи пользователя."""

from __future__ import annotations

import logging

from src.domain.entities import ContentType, Entry
from src.domain.exceptions import ValidationError
from src.domain.interfaces import EntrySaver

logger = logging.getLogger(__name__)


class SaveEntryUseCase:
    """Сценарий: пользователь отправляет текст → сохраняем → анализируем."""

    def __init__(
        self,
        repository: EntrySaver,
    ) -> None:
        self.repository = repository

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
            raise ValidationError("Нет контента для сохранения")

        entry = Entry(
            user_id=user_id,
            url=url,
            raw_text=raw_text,
            content_type=ContentType.UNKNOWN,
        )

        return await self.repository.save(entry)
