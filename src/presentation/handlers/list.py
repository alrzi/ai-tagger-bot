"""Хендлер команды /list — список последних записей."""

from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.infrastructure.db.engine import async_session_factory
from src.infrastructure.db.repositories import PostgresEntryRepository

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("list"))
async def cmd_list(message: Message) -> None:
    """Показать последние записи."""
    user_id = message.from_user.id if message.from_user else 0

    try:
        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            entries = await repo.list_recent(user_id, limit=10)

        if not entries:
            await message.answer("📋 У тебя пока нет записей.\nОтправь текст или ссылку — я сохраню!")
            return

        lines = [f"📋 Последние {len(entries)} записей:\n"]
        for entry in entries:
            tags_str = " ".join(f"#{t}" for t in entry.tags) if entry.tags else "без тегов"
            summary = entry.summary or entry.raw_text[:100]
            if entry.summary and len(entry.summary) > 100:
                summary = entry.summary[:100] + "..."
            lines.append(
                f"🆔 {entry.id}\n"
                f"📝 {summary}\n"
                f"🏷 {tags_str}\n"
            )

        await message.answer("\n".join(lines))

    except Exception as e:
        logger.error("Ошибка /list: %s", e)
        await message.answer(f"❌ Ошибка: {e}")
