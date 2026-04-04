"""Use case: сохранение записи пользователя."""

from __future__ import annotations

from src.domain.entities import Entry
from src.domain.exceptions import ValidationError
from src.domain.interfaces import EntryRepository

from src.application import log_use_case, log_db


class SaveEntryUseCase:
    """Сценарий: пользователь отправляет текст → сохраняем → анализируем."""

    def __init__(
        self,
        repository: EntryRepository,
    ) -> None:
        self.repository = repository

    async def execute(
        self,
        user_id: int,
        text: str | None = None,
        url: str | None = None,
    ) -> Entry:
        log_use_case.info(f"🚀 Начинаю SaveEntry | user_id={user_id}")

        raw_text = text or ""
        if url:
            raw_text = raw_text or url

        if not raw_text.strip():
            log_use_case.warning(f"⚠️ Пустой контент | user_id={user_id}")
            raise ValidationError("Нет контента для сохранения")

        entry = Entry(
            user_id=user_id,
            url=url,
            raw_text=raw_text,
        )

        log_db.info(f"💾 Сохраняю запись в базу | user_id={user_id}")
        saved_entry = await self.repository.save(entry)

        log_use_case.info(f"✅ Успешно сохранено | entry_id={saved_entry.id}, user_id={user_id}")
        return saved_entry
