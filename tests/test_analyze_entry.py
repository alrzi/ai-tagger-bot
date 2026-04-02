"""Тесты для AnalyzeEntryUseCase."""

from __future__ import annotations

from typing import Optional

import pytest

from src.domain.entities import AnalysisResult, ContentType, Entry
from src.application.analyze_entry import AnalyzeEntryUseCase


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


class MockAnalysisService:
    """Мок сервиса анализа."""

    def __init__(self, result: AnalysisResult | None = None, should_raise: bool = False) -> None:
        self.result = result or AnalysisResult(
            summary="Тест",
            tags=["тег"],
            content_type=ContentType.ARTICLE,
        )
        self.should_raise = should_raise
        self.analyze_called = False

    async def analyze(self, text: str) -> AnalysisResult:
        self.analyze_called = True
        if self.should_raise:
            raise Exception("Ошибка анализа")
        return self.result


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
    service = MockAnalysisService(
        result=AnalysisResult(
            summary="Python язык",
            tags=["python"],
            content_type=ContentType.ARTICLE,
        )
    )
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, analysis_service=service)

    # When
    result = await use_case.execute(entry_id=1, user_id=123)

    # Then
    assert service.analyze_called is True
    assert result.summary == "Python язык"
    assert result.tags == ["python"]
    assert result.content_type == ContentType.ARTICLE


@pytest.mark.asyncio
async def test_analyze_entry_not_found() -> None:
    # Given
    reader = MockEntryReader(None)
    updater = MockEntryUpdater()
    service = MockAnalysisService()
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, analysis_service=service)

    # When / Then
    with pytest.raises(ValueError, match="не найдена"):
        await use_case.execute(entry_id=999, user_id=123)


@pytest.mark.asyncio
async def test_analyze_empty_text() -> None:
    # Given
    entry = Entry(id=1, user_id=123, raw_text="   ")
    reader = MockEntryReader(entry)
    updater = MockEntryUpdater()
    service = MockAnalysisService()
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, analysis_service=service)

    # When / Then
    with pytest.raises(ValueError, match="Нет текста"):
        await use_case.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_service_error(sample_entry: Entry) -> None:
    # Given
    reader = MockEntryReader(sample_entry)
    updater = MockEntryUpdater()
    service = MockAnalysisService(should_raise=True)
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, analysis_service=service)

    # When / Then
    with pytest.raises(Exception, match="Ошибка анализа"):
        await use_case.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_applies_result_to_entry(sample_entry: Entry) -> None:
    # Given
    reader = MockEntryReader(sample_entry)
    updater = MockEntryUpdater()
    result = AnalysisResult(
        summary="Краткое описание",
        tags=["тег1", "тег2", "тег3"],
        content_type=ContentType.TUTORIAL,
    )
    service = MockAnalysisService(result=result)
    use_case = AnalyzeEntryUseCase(reader=reader, updater=updater, analysis_service=service)

    # When
    entry = await use_case.execute(entry_id=1, user_id=123)

    # Then
    assert entry.summary == "Краткое описание"
    assert entry.tags == ["тег1", "тег2", "тег3"]
    assert entry.content_type == ContentType.TUTORIAL
