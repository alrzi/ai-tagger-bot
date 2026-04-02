"""Интерфейсы (Protocol) для use cases."""

from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

from src.domain.entities import AnalysisResult, Entry, UserCategories

T = TypeVar("T", bound=BaseModel)


class EntryRepository(Protocol):
    """Протокол для работы с записями."""

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None: ...
    async def save(self, entry: Entry) -> Entry: ...
    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]: ...


class CategoryRepository(Protocol):
    """Протокол для работы с категориями пользователя."""

    async def get_categories(self, user_id: int) -> UserCategories: ...
    async def set_categories(self, categories: UserCategories) -> None: ...
    async def get_cached_position(self, user_id: int, tag: str) -> int | None: ...
    async def cache_position(self, user_id: int, tag: str, position: int) -> None: ...


class EmbeddingGenerator(Protocol):
    """Протокол для генерации эмбеддингов."""

    async def embed(self, text: str) -> list[float]: ...


class VectorSearcher(Protocol):
    """Протокол для векторного поиска."""

    async def search_by_vector(
        self, user_id: int, query_vector: list[float], limit: int = 5
    ) -> list[tuple[Entry, float]]: ...


class EntryAnalysisService(Protocol):
    """Протокол сервиса анализа текста."""

    async def analyze(self, text: str) -> AnalysisResult: ...


class AIClient(Protocol):
    """Протокол для ИИ-клиента."""

    async def generate_structured(self, prompt: str, schema: type[T], system: str | None = None) -> T: ...
