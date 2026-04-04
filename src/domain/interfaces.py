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
    async def get_stats(self, user_id: int) -> dict[int, int]: ...


class EmbeddingGenerator(Protocol):
    """Протокол для генерации эмбеддингов."""

    async def embed(self, text: str) -> list[float]: ...


class VectorSearcher(Protocol):
    """Протокол для векторного поиска."""
    
    async def search_with_chunks(
        self, 
        user_id: int, 
        query_vector: list[float], 
        category_id: int | None = None, 
        limit: int = 5
    ) -> list[dict[str, object]]: ...


class EntryAnalysisService(Protocol):
    """Протокол сервиса анализа текста."""

    async def analyze(self, text: str, categories: UserCategories, existing_tags: list[str]) -> AnalysisResult: ...


class TagRepository(Protocol):
    """Протокол для работы с тегами."""

    async def get_all_user_tags(self, user_id: int) -> list[str]: ...
    async def find_by_normalized_names(self, user_id: int, normalized_names: list[str]) -> dict[str, int]: ...
    async def create_many(self, user_id: int, tags: list[tuple[str, str]]) -> dict[str, int]: ...
    async def replace_entry_tags(self, entry_id: int, tag_ids: list[int]) -> None: ...
    async def get_tags_for_entries(self, entry_ids: list[int]) -> dict[int, list[str]]: ...


class ChunkRepository(Protocol):
    """Протокол для работы с чанками текста."""

    async def create(self, entry_id: int, text: str, embedding: list[float], position: int) -> None: ...
    async def save_chunks(self, entry_id: int, chunks: list[tuple[str, list[float]]]) -> None: ...
    async def delete_by_entry_id(self, entry_id: int) -> None: ...


class AIClient(Protocol):
    """Протокол для ИИ-клиента."""

    async def generate_structured(self, prompt: str, schema: type[T], system: str | None = None) -> T: ...
