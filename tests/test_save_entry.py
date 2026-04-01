"""Тесты для SaveEntryUseCase."""

from __future__ import annotations

from typing import Optional

import pytest

from src.domain.entities import Entry
from src.usecases.save_entry import SaveEntryUseCase


class MockEntryRepository:
    """Мок-репозиторий для тестов."""

    def __init__(self) -> None:
        self.saved_entry: Optional[Entry] = None
        self.save_called = False

    async def save(self, entry: Entry) -> Entry:
        self.save_called = True
        entry.id = 1
        self.saved_entry = entry
        return entry


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
    assert mock_repo.save_called is True
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
    with pytest.raises(ValueError, match="Нет контента"):
        await use_case.execute(user_id=user_id, text=text)


@pytest.mark.asyncio
async def test_save_none_text_raises_error(use_case: SaveEntryUseCase) -> None:
    # Given
    user_id = 123

    # When / Then
    with pytest.raises(ValueError, match="Нет контента"):
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
    assert repo.saved_entry is not None
    assert repo.saved_entry.tags == ["python", "тестирование"]
    assert repo.saved_entry.summary == "Тестовое резюме"
