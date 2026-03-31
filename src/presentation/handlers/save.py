"""Хендлер для приёма текстовых сообщений и ссылок."""

from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.types import Message

from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.db.engine import async_session_factory
from src.infrastructure.db.repositories import PostgresEntryRepository
from src.usecases.analyze_entry import AnalyzeEntryUseCase
from src.usecases.save_entry import SaveEntryUseCase

router = Router()

URL_PATTERN = re.compile(r"https?://\S+")


def _extract_url(text: str) -> str | None:
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


@router.message(F.text)
async def handle_text(message: Message) -> None:
    """Ловит текстовые сообщения и ссылки."""
    if message.text is None:
        return

    user_id = message.from_user.id if message.from_user else 0
    text = message.text
    url = _extract_url(text)

    try:
        async with async_session_factory() as session:
            repo = PostgresEntryRepository(session)
            ollama = OllamaClient()
            analyzer = AnalyzeEntryUseCase(
                reader=repo,
                updater=repo,
                ai_client=ollama,
            )
            use_case = SaveEntryUseCase(repository=repo, analyzer=analyzer)
            entry = await use_case.execute(
                user_id=user_id,
                text=text if not url else None,
                url=url,
            )

        tags_str = " ".join(f"#{t}" for t in entry.tags) if entry.tags else ""
        await message.answer(
            f"✅ Сохранено!\n"
            f"🆔 ID: {entry.id}\n"
            f"📝 {entry.summary or entry.raw_text[:100]}\n"
            f"🏷 {tags_str}"
        )
    except ValueError as e:
        await message.answer(f"❌ {e}")
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {e}")
