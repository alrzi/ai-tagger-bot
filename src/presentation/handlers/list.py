"""Хендлер команды /list — список последних записей."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from src.presentation.presenters.entry_presenter import EntryPresenterProtocol
from src.usecases.list_entries import ListEntriesUseCase

router = Router()


@router.message(Command("list"))
async def cmd_list(
    message: Message,
    use_case: FromDishka[ListEntriesUseCase],
    presenter: FromDishka[EntryPresenterProtocol],
) -> None:
    """Показать последние записи."""
    user_id = message.from_user.id if message.from_user else 0
    entries = await use_case.execute(user_id)

    if not entries:
        await message.answer(
            "📋 У тебя пока нет записей.\nОтправь текст или ссылку — я сохраню!"
        )
        return

    await message.answer(presenter.format_list(entries))
