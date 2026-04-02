"""Use case: семантический поиск записей."""

from __future__ import annotations

from src.domain.dto import EntryDTO
from src.domain.interfaces import EmbeddingGenerator, VectorSearcher


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
        limit: int = 5,
    ) -> list[tuple[EntryDTO, float]]:
        query_vector = await self.embedder.embed(query)
        results = await self.searcher.search_by_vector(user_id, query_vector, limit)
        return [(EntryDTO.from_entity(entry), similarity) for entry, similarity in results]
