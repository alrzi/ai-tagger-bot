"""Taskiq воркер для фоновых задач."""

from __future__ import annotations

import logging

from aiogram import Bot
from dishka import FromDishka
from dishka.integrations.taskiq import inject, setup_dishka
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from config.settings import settings
from src.application.analyze_entry import AnalyzeEntryInteractor
from src.domain.entities import Entry
from src.domain.exceptions import NotFoundError, ValidationError
from src.ioc.container import make_container
from src.presentation.context import WorkerBotContext
from src.presentation.responders.analyze_result_responder import AnalyzeResultResponder

logger = logging.getLogger(__name__)

# Redis broker для очереди задач
broker = RedisStreamBroker(settings.redis_url).with_result_backend(
    RedisAsyncResultBackend(settings.redis_url),
)

# Настраиваем Dishka для Taskiq
container = make_container()
setup_dishka(container, broker)


@broker.task(
    task_name="analyze_entry",
    retry_on_error=True,
    max_retries=3,
)
@inject
async def analyze_entry_task(
    entry_id: int,
    user_id: int,
    interactor: FromDishka[AnalyzeEntryInteractor],
    bot: FromDishka[Bot],
    responder: FromDishka[AnalyzeResultResponder],
) -> dict[str, object]:
    """Фоновая задача анализа записи через ИИ."""
    result = await _analyze_entry_logic(entry_id, user_id, interactor)

    if isinstance(result, Entry):
        ctx = WorkerBotContext(bot, user_id)
        await responder.respond(result, ctx)
        return {"entry_id": entry_id, "status": "success"}

    return result


async def _analyze_entry_logic(
    entry_id: int,
    user_id: int,
    interactor: AnalyzeEntryInteractor,
) -> Entry | dict[str, object]:
    """Бизнес-логика анализа записи."""
    try:
        return await interactor.execute(entry_id, user_id)
    except (NotFoundError, ValidationError) as exc:
        logger.warning("Задача отменена: %s", exc)
        return {"status": "cancelled", "reason": str(exc)}
