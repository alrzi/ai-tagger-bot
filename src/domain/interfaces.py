"""Интерфейсы (Protocol) для use cases."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from src.domain.entities import AnalysisResult, Entry, UserCategories

T = TypeVar("T", bound=BaseModel)


class EntryRepository(ABC):
    """Интерфейс для работы с записями."""

    @abstractmethod
    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None: ...

    @abstractmethod
    async def save(self, entry: Entry) -> Entry: ...

    @abstractmethod
    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]: ...


class CategoryRepository(ABC):
    """Интерфейс для работы с категориями пользователя."""

    @abstractmethod
    async def get_categories(self, user_id: int) -> UserCategories: ...

    @abstractmethod
    async def set_categories(self, categories: UserCategories) -> None: ...

    @abstractmethod
    async def get_stats(self, user_id: int) -> dict[int, int]: ...


class EmbeddingGenerator(ABC):
    """Интерфейс для генерации эмбеддингов."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...


class VectorSearcher(ABC):
    """Интерфейс для векторного поиска."""
    
    @abstractmethod
    async def search_with_chunks(
        self, 
        user_id: int, 
        query_vector: list[float], 
        category_id: int | None = None, 
        limit: int = 5
    ) -> list[dict[str, object]]: ...


class EntryAnalysisService(ABC):
    """Интерфейс сервиса анализа текста."""

    @abstractmethod
    async def analyze(self, text: str, categories: UserCategories, existing_tags: list[str]) -> AnalysisResult: ...


class TagRepository(ABC):
    """Интерфейс для работы с тегами."""

    @abstractmethod
    async def get_all_user_tags(self, user_id: int) -> list[str]: ...

    @abstractmethod
    async def find_by_normalized_names(self, user_id: int, normalized_names: list[str]) -> dict[str, int]: ...

    @abstractmethod
    async def create_many(self, user_id: int, tags: list[tuple[str, str]]) -> dict[str, int]: ...

    @abstractmethod
    async def replace_entry_tags(self, entry_id: int, tag_ids: list[int]) -> None: ...

    @abstractmethod
    async def get_tags_for_entries(self, entry_ids: list[int]) -> dict[int, list[str]]: ...


class ChunkRepository(ABC):
    """Интерфейс для работы с чанками текста."""

    @abstractmethod
    async def save_chunks(self, entry_id: int, chunks: list[tuple[str, list[float]]]) -> None: ...

    @abstractmethod
    async def delete_by_entry_id(self, entry_id: int) -> None: ...


class AIClient(ABC):
    """Интерфейс для ИИ-клиента."""

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: type[T], system: str | None = None) -> T: ...
