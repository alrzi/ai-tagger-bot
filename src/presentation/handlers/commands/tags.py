"""Хендлер команды /tags — список всех тегов пользователя."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from src.application.get_all_tags import GetAllTagsUseCase
from src.presentation.context import TelegramChatContext
from src.presentation.responders.tags_responder import TagsResponder

router = Router()


@router.message(Command("tags"))
async def cmd_tags(
    message: Message,
    use_case: FromDishka[GetAllTagsUseCase],
    responder: FromDishka[TagsResponder],
) -> None:
    """Показать все теги пользователя."""
    ctx = TelegramChatContext(message)
    tags = await use_case.execute(ctx.user_id)
    await responder.respond(tags, ctx)
