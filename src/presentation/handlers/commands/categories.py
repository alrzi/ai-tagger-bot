"""Хендлер команды /categories — управление категориями ромба."""

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from dishka import FromDishka

from src.application.manage_categories import ManageCategoriesUseCase
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
    args = command.args

    if args is None:
        # /categories — показать текущие
        categories = await use_case.get(ctx.user_id)
        await responder.respond(categories, ctx)
        return

    parts = args.split(maxsplit=1)
    subcommand = parts[0].lower()

    if subcommand == "reset":
        # /categories reset
        categories = await use_case.reset(ctx.user_id)
        await responder.respond_updated(categories, ctx)

    elif subcommand == "set":
        # /categories set Кат1 Кат2 Кат3 Кат4 Кат5
        if len(parts) < 2:
            await message.answer(
                "Укажи 5 категорий через пробел.\n"
                "Пример: /categories set Python AI Здоровье Бизнес Креатив"
            )
            return

        names = parts[1].split()
        categories = await use_case.set(ctx.user_id, names)
        await responder.respond_updated(categories, ctx)

    else:
        await message.answer(
            "Использование:\n"
            "/categories — показать текущие\n"
            "/categories set Кат1 Кат2 Кат3 Кат4 Кат5 — установить\n"
            "/categories reset — сбросить на стандартные"
        )
