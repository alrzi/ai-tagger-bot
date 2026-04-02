"""Хендлер callback для отображения полной записи."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka import FromDishka

from src.domain.exceptions import ParseError
from src.presentation.presenters.entry_presenter import EntryPresenterProtocol
from src.usecases.get_entry import GetEntryUseCase

router = Router()


@router.callback_query(F.data.startswith("entry:"))
async def callback_show_entry(
    callback: CallbackQuery,
    use_case: FromDishka[GetEntryUseCase],
    presenter: FromDishka[EntryPresenterProtocol],
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

    user_id = callback.from_user.id
    entry = await use_case.execute(entry_id, user_id)

    if callback.message is not None:
        await callback.message.answer(presenter.format_full(entry))
    await callback.answer()
