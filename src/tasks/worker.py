"""Taskiq воркер для фоновых задач."""

from __future__ import annotations

import logging

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from config.settings import settings

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
async def analyze_entry_task(entry_id: int, user_id: int) -> dict[str, object]:
    """Фоновая задача анализа записи через ИИ."""
    from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
    from src.infrastructure.ai.embeddings import OllamaEmbeddingService
    from src.infrastructure.ai.ollama_client import OllamaClient
    from src.infrastructure.db.engine import async_session_factory
    from src.infrastructure.db.repositories import PostgresEntryRepository
    from src.usecases.analyze_entry import AnalyzeEntryUseCase

    async with async_session_factory() as session:
        repo = PostgresEntryRepository(session)
        ollama = OllamaClient()
        analysis_service = OllamaEntryAnalysisService(ai_client=ollama)
        analyzer = AnalyzeEntryUseCase(
            reader=repo,
            updater=repo,
            analysis_service=analysis_service,
        )
        entry = await analyzer.execute(entry_id, user_id)

        # Генерация эмбеддинга
        embedder = OllamaEmbeddingService()
        text_for_embedding = entry.summary or entry.raw_text
        embedding = await embedder.embed(text_for_embedding[:2000])
        await repo.update_embedding(entry_id, embedding)

    return {
        "entry_id": entry_id,
        "status": "success",
        "tags": entry.tags,
        "summary": entry.summary,
    }
