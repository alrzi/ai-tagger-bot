"""Хендлер команды /list — список последних записей."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from src.application.list_entries import ListEntriesUseCase
from src.presentation.context import TelegramChatContext
from src.presentation.responders.list_responder import ListEntriesResponder

router = Router()


@router.message(Command("list"))
async def cmd_list(
    message: Message,
    use_case: FromDishka[ListEntriesUseCase],
    responder: FromDishka[ListEntriesResponder],
) -> None:
    """Показать последние записи."""
    ctx = TelegramChatContext(message)
    entries = await use_case.execute(ctx.user_id)
    await responder.respond(entries, ctx)
