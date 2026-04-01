"""Хендлер для приёма текстовых сообщений и ссылок."""

from __future__ import annotations

import asyncio
import logging
import re

from aiogram import F, Router
from aiogram.types import Message

from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.db.engine import async_session_factory
from src.infrastructure.db.repositories import PostgresEntryRepository
from src.usecases.analyze_entry import AnalyzeEntryUseCase
from src.usecases.save_entry import SaveEntryUseCase

logger = logging.getLogger(__name__)
router = Router()

URL_PATTERN = re.compile(r"https?://\S+")


def _extract_url(text: str) -> str | None:
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


async def _analyze_in_background(
    entry_id: int,
    user_id: int,
    message: Message,
) -> None:
    """Фоновый анализ записи с уведомлением пользователя."""
    try:
        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            ollama = OllamaClient()
            analysis_service = OllamaEntryAnalysisService(ai_client=ollama)
            analyzer = AnalyzeEntryUseCase(
                reader=repo,
                updater=repo,
                analysis_service=analysis_service,
            )
            entry = await analyzer.execute(entry_id, user_id)

        tags_str = " ".join(f"#{t}" for t in entry.tags) if entry.tags else ""
        await message.answer(
            f"✅ Анализ завершён для ID {entry_id}!\n"
            f"📝 {entry.summary}\n"
            f"🏷 {tags_str}"
        )
    except Exception as e:
        logger.warning("Ошибка фонового анализа записи %s: %s", entry_id, e)
        try:
            await message.answer(
                f"⚠️ Не удалось проанализировать запись ID {entry_id}:\n"
                f"{e}\n"
                f"Запись сохранена, но без тегов и резюме."
            )
        except Exception:
            await message.answer(
                f"⚠️ Не удалось проанализировать запись ID {entry_id}:\n"                
                f"Запись сохранена, но без тегов и резюме."
            )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """Ловит текстовые сообщения и ссылки."""
    if message.text is None:
        return

    user_id = message.from_user.id if message.from_user else 0
    text = message.text
    url = _extract_url(text)

    try:
        # Сохраняем сразу (без анализа)
        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            use_case = SaveEntryUseCase(repository=repo)
            entry = await use_case.execute(
                user_id=user_id,
                text=text if not url else None,
                url=url,
            )

        await message.answer(
            f"✅ Сохранено! ID: {entry.id}\n"
            f"⏳ Анализирую через ИИ..."
        )

        # Запускаем анализ в фоне
        if entry.id:
            asyncio.create_task(
                _analyze_in_background(entry.id, user_id, message)
            )

    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {e}")
