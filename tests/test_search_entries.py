"""Тесты для SearchEntriesUseCase."""

from __future__ import annotations

import pytest

from src.domain.entities import Entry
from src.application.search_entries import SearchEntriesUseCase


class MockEmbedder:
    """Мок для генератора эмбеддингов."""

    def __init__(self, embedding: list[float] | None = None) -> None:
        self.embedding = embedding or [0.1] * 4096
        self.embed_called = False
        self.embed_text: str | None = None

    async def embed(self, text: str) -> list[float]:
        self.embed_called = True
        self.embed_text = text
        return self.embedding


class MockSearcher:
    """Мок для поисковика."""

    def __init__(self, results: list[tuple[Entry, float]] | None = None) -> None:
        self.results = results or []
        self.search_called = False
        self.search_args: tuple = ()

    async def search_by_vector(
        self, user_id: int, query_vector: list[float], limit: int = 5
    ) -> list[tuple[Entry, float]]:
        self.search_called = True
        self.search_args = (user_id, query_vector, limit)
        return self.results


@pytest.mark.asyncio
async def test_search_calls_embedder_and_searcher() -> None:
    """Тест: use case вызывает embedder и searcher."""
    # Given
    embedder = MockEmbedder()
    searcher = MockSearcher()
    use_case = SearchEntriesUseCase(embedder=embedder, searcher=searcher)

    # When
    await use_case.execute(user_id=123, query="python программирование", limit=5)

    # Then
    assert embedder.embed_called is True
    assert embedder.embed_text == "python программирование"
    assert searcher.search_called is True
    assert searcher.search_args[0] == 123  # user_id
    assert searcher.search_args[2] == 5  # limit


@pytest.mark.asyncio
async def test_search_returns_results() -> None:
    """Тест: use case возвращает результаты поиска."""
    # Given
    entry = Entry(id=1, user_id=123, tags=["python", "programming"])
    embedder = MockEmbedder()
    searcher = MockSearcher(results=[(entry, 0.95)])
    use_case = SearchEntriesUseCase(embedder=embedder, searcher=searcher)

    # When
    results = await use_case.execute(user_id=123, query="python", limit=5)

    # Then
    assert len(results) == 1
    assert results[0][0].id == 1
    assert results[0][0].tags == ["python", "programming"]
    assert results[0][1] == 0.95  # similarity score


@pytest.mark.asyncio
async def test_search_empty_results() -> None:
    """Тест: use case возвращает пустой список если ничего не найдено."""
    # Given
    embedder = MockEmbedder()
    searcher = MockSearcher(results=[])
    use_case = SearchEntriesUseCase(embedder=embedder, searcher=searcher)

    # When
    results = await use_case.execute(user_id=123, query="несуществующий запрос", limit=5)

    # Then
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_passes_embedding_to_searcher() -> None:
    """Тест: use case передаёт эмбеддинг запроса в searcher."""
    # Given
    test_embedding = [0.5, 0.3, 0.2]
    embedder = MockEmbedder(embedding=test_embedding)
    searcher = MockSearcher()
    use_case = SearchEntriesUseCase(embedder=embedder, searcher=searcher)

    # When
    await use_case.execute(user_id=123, query="тест", limit=3)

    # Then
    assert searcher.search_called is True
    assert searcher.search_args[1] == test_embedding  # query_vector
