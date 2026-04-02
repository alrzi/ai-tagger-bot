"""Хендлер команды /search — семантический поиск."""

from aiogram import F, Router
from aiogram.types import Message
from dishka import FromDishka

from src.application.search_entries import SearchEntriesUseCase
from src.presentation.context import TelegramChatContext
from src.presentation.responders.search_responder import SearchEntriesResponder

router = Router()


@router.message(F.text.startswith("/search"))
async def cmd_search(
    message: Message,
    use_case: FromDishka[SearchEntriesUseCase],
    responder: FromDishka[SearchEntriesResponder],
) -> None:
    """Семантический поиск по записям."""
    if message.text is None:
        return

    query = message.text.replace("/search", "", 1).strip()
    if not query:
        await message.answer(
            "Использование: /search <запрос>\nПример: /search как найти работу"
        )
        return

    ctx = TelegramChatContext(message)
    results = await use_case.execute(user_id=ctx.user_id, query=query, limit=3)
    await responder.respond(results, ctx)
