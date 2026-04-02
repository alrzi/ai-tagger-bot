"""Taskiq воркер для фоновых задач."""

from __future__ import annotations

import logging

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from config.settings import settings
from src.application.analyze_entry import AnalyzeEntryInteractor

logger = logging.getLogger(__name__)

# Redis broker для очереди задач
broker = RedisStreamBroker(settings.redis_url).with_result_backend(
    RedisAsyncResultBackend(settings.redis_url),
)


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
) -> dict[str, object]:
    """Фоновая задача анализа записи через ИИ."""
    entry = await interactor.execute(entry_id, user_id)

    return {
        "entry_id": entry_id,
        "status": "success",
        "tags": entry.tags,
        "summary": entry.summary,
    }
