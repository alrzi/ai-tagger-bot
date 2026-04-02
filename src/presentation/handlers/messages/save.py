"""Хендлер для приёма текстовых сообщений и ссылок."""

from aiogram import F, Router
from aiogram.types import Message
from dishka import FromDishka

from src.application.save_entry import SaveEntryUseCase
from src.presentation.context import TelegramChatContext
from src.presentation.responders.save_responder import SaveEntryResponder
from src.tasks.worker import analyze_entry_task

router = Router()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(
    message: Message,
    save_use_case: FromDishka[SaveEntryUseCase],
    responder: FromDishka[SaveEntryResponder],
) -> None:
    """Ловит текстовые сообщения и ссылки (не команды)."""
    if message.text is None:
        return

    ctx = TelegramChatContext(message)
    entry = await save_use_case.execute(
        user_id=ctx.user_id,
        text=message.text,
    )
    await responder.respond(entry, ctx)

    if entry.id:
        await analyze_entry_task.kiq(entry_id=entry.id, user_id=ctx.user_id)
