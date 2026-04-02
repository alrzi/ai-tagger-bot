"""Хендлер callback для отображения полной записи."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka import FromDishka

from src.application.get_entry import GetEntryUseCase
from src.domain.exceptions import ParseError
from src.presentation.context import TelegramChatContext
from src.presentation.responders.entry_responder import EntryResponder

router = Router()


@router.callback_query(F.data.startswith("entry:"))
async def callback_show_entry(
    callback: CallbackQuery,
    use_case: FromDishka[GetEntryUseCase],
    responder: FromDishka[EntryResponder],
) -> None:
    """Показать полную запись по ID."""
    if callback.data is None:
        raise ParseError("Некорректный ID записи")

    parts = callback.data.split(":")
    if len(parts) < 2:
        raise ParseError("Некорректный ID записи")

    try:
        entry_id = int(parts[1])
    except ValueError:
        raise ParseError("Некорректный ID записи")

    ctx = TelegramChatContext(callback)
    entry = await use_case.execute(entry_id, ctx.user_id)
    await responder.respond(entry, ctx)
