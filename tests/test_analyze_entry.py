"""Тесты для AnalyzeEntryUseCase."""

from __future__ import annotations

from typing import Optional

import pytest

from src.domain.entities import ContentType, Entry
from src.usecases.analyze_entry import AnalyzeEntryUseCase


class MockEntryReader:
    """Мок-репозиторий для чтения."""

    def __init__(self, entry: Entry | None = None) -> None:
        self.entry = entry

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None:
        return self.entry


class MockEntryUpdater:
    """Мок-репозиторий для обновления."""

    def __init__(self) -> None:
        self.saved_entry: Optional[Entry] = None

    async def save(self, entry: Entry) -> Entry:
        self.saved_entry = entry
        return entry


class MockAIClient:
    """Мок ИИ-клиента."""

    def __init__(self, response: str = '{"summary": "Тест", "tags": ["тег"], "type": "article"}') -> None:
        self.response = response
        self.generate_called = False

    async def generate(self, prompt: str) -> str:
        self.generate_called = True
        return self.response


@pytest.fixture
def sample_entry() -> Entry:
    return Entry(
        id=1,
        user_id=123,
        raw_text="Python — язык программирования",
        content_type=ContentType.UNKNOWN,
    )


@pytest.mark.asyncio
async def test_analyze_success(sample_entry: Entry) -> None:
    # Given
    reader = MockEntryReader(sample_entry)
    updater = MockEntryUpdater()
    ai = MockAIClient('{"summary": "Python язык", "tags": ["python"], "type": "article"}')
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, ai_client=ai)

    # When
    result = await use_case.execute(entry_id=1, user_id=123)

    # Then
    assert ai.generate_called is True
    assert result.summary == "Python язык"
    assert result.tags == ["python"]
    assert result.content_type == ContentType.ARTICLE


@pytest.mark.asyncio
async def test_analyze_entry_not_found() -> None:
    # Given
    reader = MockEntryReader(None)
    updater = MockEntryUpdater()
    ai = MockAIClient()
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, ai_client=ai)

    # When / Then
    with pytest.raises(ValueError, match="не найдена"):
        await use_case.execute(entry_id=999, user_id=123)


@pytest.mark.asyncio
async def test_analyze_empty_text() -> None:
    # Given
    entry = Entry(id=1, user_id=123, raw_text="   ")
    reader = MockEntryReader(entry)
    updater = MockEntryUpdater()
    ai = MockAIClient()
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, ai_client=ai)

    # When / Then
    with pytest.raises(ValueError, match="Нет текста"):
        await use_case.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_invalid_json(sample_entry: Entry) -> None:
    # Given
    reader = MockEntryReader(sample_entry)
    updater = MockEntryUpdater()
    ai = MockAIClient("not valid json")
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, ai_client=ai)

    # When
    result = await use_case.execute(entry_id=1, user_id=123)

    # Then — fallback значения
    assert result.summary == "Не удалось проанализировать"
    assert result.tags == []
