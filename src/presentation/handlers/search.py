"""Хендлер команды /search — семантический поиск."""

from aiogram import F, Router
from aiogram.types import Message
from dishka import FromDishka

from src.presentation.keyboards.inline import search_results_keyboard
from src.presentation.presenters.entry_presenter import EntryPresenterProtocol
from src.usecases.search_entries import SearchEntriesUseCase

router = Router()


@router.message(F.text.startswith("/search"))
async def cmd_search(
    message: Message,
    use_case: FromDishka[SearchEntriesUseCase],
    presenter: FromDishka[EntryPresenterProtocol],
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

    user_id = message.from_user.id if message.from_user else 0
    results = await use_case.execute(user_id=user_id, query=query, limit=5)

    if not results:
        await message.answer("🔍 Ничего не найдено. Попробуй другой запрос.")
        return

    text, entry_ids = presenter.format_search(results)
    await message.answer(text, reply_markup=search_results_keyboard(entry_ids))
