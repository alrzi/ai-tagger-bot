"""Use case: семантический поиск записей."""

from __future__ import annotations

from src.domain.interfaces import EmbeddingGenerator, VectorSearcher
from src.application import log_use_case, log_ai


class SearchEntriesUseCase:
    """Сценарий: пользователь ищет по смыслу → находим похожие записи."""

    def __init__(
        self,
        embedder: EmbeddingGenerator,
        searcher: VectorSearcher,
    ) -> None:
        self.embedder = embedder
        self.searcher = searcher

    async def execute(
        self,
        user_id: int,
        query: str,
        category_id: int | None = None,
        limit: int = 5,
    ) -> list[dict[str, object]]:
        """Возвращает список с результатами поиска: Запись + Чанк + Расстояние."""
        log_use_case.info(f"🔍 Начинаю SearchEntries | user_id={user_id}, limit={limit}")
        log_ai.info(f"🧠 Генерирую эмбеддинг запроса | query='{query[:30]}...'")
        
        query_vector = await self.embedder.embed(query)
        results = await self.searcher.search_with_chunks(user_id, query_vector, category_id, limit)
        
        log_use_case.info(f"✅ Поиск завершен | найдено {len(results)} результатов")
        return results
