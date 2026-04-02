"""Хендлер для приёма текстовых сообщений и ссылок."""

from aiogram import F, Router
from aiogram.types import Message
from dishka import FromDishka

from src.tasks.worker import analyze_entry_task
from src.usecases.save_entry import SaveEntryUseCase

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(
    message: Message,
    save_use_case: FromDishka[SaveEntryUseCase],
) -> None:
    """Ловит текстовые сообщения и ссылки (не команды)."""
    if message.text is None:
        return

    user_id = message.from_user.id if message.from_user else 0
    entry = await save_use_case.execute(
        user_id=user_id,
        text=message.text,
    )

    await message.answer(
        f"✅ Сохранено! ID: {entry.id}\n"
        f"⏳ Анализирую через ИИ..."
    )

    if entry.id:
        await analyze_entry_task.kiq(entry_id=entry.id, user_id=user_id)
