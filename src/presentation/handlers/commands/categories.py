"""Хендлер команды /categories — управление категориями ромба."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from dishka import FromDishka

from src.application.manage_categories import ManageCategoriesUseCase
from src.domain.exceptions import ValidationError
from src.presentation.context import TelegramChatContext
from src.presentation.responders.categories_responder import CategoriesResponder

router = Router()


@router.message(Command("categories"))
async def cmd_categories(
    message: Message,
    command: CommandObject,
    use_case: FromDishka[ManageCategoriesUseCase],
    responder: FromDishka[CategoriesResponder],
) -> None:
    """Управление категориями для ромба."""
    ctx = TelegramChatContext(message)

    if not command.args:
        categories = await use_case.get(ctx.user_id)
        await responder.respond(categories, ctx)
        return

    try:
        categories = await use_case.handle_command(ctx.user_id, command.args)
        await responder.respond_updated(categories, ctx)
    except ValidationError as exc:
        await message.answer(str(exc))
