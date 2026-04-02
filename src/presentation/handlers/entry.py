"""Хендлер callback для отображения полной записи."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.infrastructure.db.engine import async_session_factory
from src.infrastructure.db.repositories import PostgresEntryRepository

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("entry:"))
async def callback_show_entry(callback: CallbackQuery) -> None:
    """Показать полную запись по ID."""
    if callback.data is None:
        await callback.answer("Некорректный ID записи", show_alert=True)
        return

    try:
        entry_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректный ID записи", show_alert=True)
        return

    user_id = callback.from_user.id

    try:
        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            entry = await repo.get_by_id(entry_id, user_id)

        if entry is None:
            await callback.answer("Запись не найдена", show_alert=True)
            return

        # Форматируем полный текст
        tags_str = " ".join(f"#{t}" for t in entry.tags) if entry.tags else "без тегов"
        full_text = (
            f"📝 Запись #{entry.id}\n\n"
            f"{entry.raw_text}\n\n"
            f"🏷 {tags_str}\n"
            f"📂 Тип: {entry.content_type.value}\n"
        )
        if entry.url:
            full_text += f"🔗 {entry.url}\n"
        if entry.summary:
            full_text += f"\n📋 Резюме:\n{entry.summary}\n"

        if callback.message is not None:
            await callback.message.answer(full_text)
        await callback.answer()

    except Exception as e:
        logger.error("Ошибка отображения записи: %s", e)
        await callback.answer("Произошла ошибка при загрузке записи", show_alert=True)
