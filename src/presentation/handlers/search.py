"""Хендлер команды /search — семантический поиск."""

from __future__ import annotations

import logging
import traceback

from aiogram import F, Router
from aiogram.types import Message

from src.infrastructure.ai.embeddings import OllamaEmbeddingService
from src.infrastructure.db.engine import async_session_factory
from src.infrastructure.db.repositories import PostgresEntryRepository
from src.usecases.search_entries import SearchEntriesUseCase

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.startswith("/search"))
async def cmd_search(message: Message) -> None:
    """Семантический поиск по записям."""
    logger.info("Хендлер search сработал, текст: %s", message.text)

    if message.text is None:
        logger.warning("Сообщение без текста, игнорирую")
        return

    # Извлекаем запрос после /search
    query = message.text.replace("/search", "", 1).strip()
    if not query:
        await message.answer("Использование: /search <запрос>\nПример: /search как найти работу")
        return

    user_id = message.from_user.id if message.from_user else 0

    try:
        logger.info("Поиск: '%s', user_id: %s", query, user_id)

        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            embedder = OllamaEmbeddingService()
            use_case = SearchEntriesUseCase(embedder=embedder, searcher=repo)
            results = await use_case.execute(user_id=user_id, query=query, limit=5)

        logger.info("Найдено записей: %d", len(results))

        if not results:
            await message.answer("🔍 Ничего не найдено. Попробуй другой запрос.")
            return

        lines = [f"🔍 Найдено {len(results)} записей:\n"]
        for entry, similarity in results:
            tags_str = " ".join(f"#{t}" for t in entry.tags) if entry.tags else ""
            lines.append(
                f"🆔 {entry.id} ({similarity:.0%})\n"
                f"📝 {entry.summary or entry.raw_text[:80]}\n"
                f"🏷 {tags_str}\n"
            )

        await message.answer("\n".join(lines))

    except Exception as e:
        logger.error("Ошибка поиска: %s\n%s", e, traceback.format_exc())
        await message.answer(f"❌ Ошибка поиска: {e}")
