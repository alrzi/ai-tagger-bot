"""Хендлер команды /stats — статистика по категориям."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka

from src.application.get_stats import GetStatsUseCase
from src.presentation.context import TelegramChatContext
from src.presentation.responders.stats_responder import StatsResponder

router = Router()


@router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    use_case: FromDishka[GetStatsUseCase],
    responder: FromDishka[StatsResponder],
) -> None:
    """Показать статистику по категориям."""
    ctx = TelegramChatContext(message)
    categories, stats = await use_case.execute(ctx.user_id)
    await responder.respond(categories, stats, ctx)
