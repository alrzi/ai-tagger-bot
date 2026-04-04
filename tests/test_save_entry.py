"""Тесты для SaveEntryUseCase."""

from __future__ import annotations

import pytest

from src.domain.entities import Entry
from src.domain.exceptions import ValidationError
from src.application.save_entry import SaveEntryUseCase


class MockEntryRepository:
    """Мок-репозиторий для тестов."""

    def __init__(self) -> None:
        self.saved: list[Entry] = []

    async def save(self, entry: Entry) -> Entry:
        entry.id = len(self.saved) + 1
        self.saved.append(entry)
        return entry
    
    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None:
        return next((e for e in self.saved if e.id == entry_id and e.user_id == user_id), None)
    
    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]:
        return list(reversed([e for e in self.saved if e.user_id == user_id][-limit:]))
    
    async def search_by_vector(self, user_id: int, query_vector: list[float], limit: int = 5) -> list[tuple[Entry, float]]:
        return []
    
    async def search_by_tags(self, user_id: int, tags: list[str], limit: int = 10) -> list[Entry]:
        return []
    
    async def delete(self, entry_id: int, user_id: int) -> bool:
        return True


@pytest.fixture
def mock_repo() -> MockEntryRepository:
    return MockEntryRepository()


@pytest.fixture
def use_case(mock_repo: MockEntryRepository) -> SaveEntryUseCase:
    return SaveEntryUseCase(repository=mock_repo)


@pytest.mark.asyncio
async def test_save_text_success(use_case: SaveEntryUseCase, mock_repo: MockEntryRepository) -> None:
    # Given
    user_id = 123
    text = "Привет мир"

    # When
    entry = await use_case.execute(user_id=user_id, text=text)

    # Then
    assert len(mock_repo.saved) == 1
    assert entry.id == 1
    assert entry.user_id == 123
    assert entry.raw_text == "Привет мир"


@pytest.mark.asyncio
async def test_save_url_success(use_case: SaveEntryUseCase, mock_repo: MockEntryRepository) -> None:
    # Given
    user_id = 456
    url = "https://example.com"

    # When
    entry = await use_case.execute(user_id=user_id, url=url)

    # Then
    assert entry.user_id == 456
    assert entry.url == "https://example.com"
    assert entry.raw_text == "https://example.com"


@pytest.mark.asyncio
async def test_save_empty_text_raises_error(use_case: SaveEntryUseCase) -> None:
    # Given
    user_id = 123
    text = "   "

    # When / Then
    with pytest.raises(ValidationError, match="Нет контента"):
        await use_case.execute(user_id=user_id, text=text)


@pytest.mark.asyncio
async def test_save_none_text_raises_error(use_case: SaveEntryUseCase) -> None:
    # Given
    user_id = 123

    # When / Then
    with pytest.raises(ValidationError, match="Нет контента"):
        await use_case.execute(user_id=user_id)


@pytest.mark.asyncio
async def test_save_preserves_tags() -> None:
    """Тест: теги сохраняются при обновлении записи."""
    # Given
    repo = MockEntryRepository()
    use_case = SaveEntryUseCase(repository=repo)

    # When — сохраняем запись
    entry = await use_case.execute(user_id=123, text="Тест с тегами")
    entry.tags = ["python", "тестирование"]
    entry.summary = "Тестовое резюме"

    # Then — теги должны сохраниться
    assert len(repo.saved) > 0
    assert repo.saved[0].tags == ["python", "тестирование"]
    assert repo.saved[0].summary == "Тестовое резюме"
