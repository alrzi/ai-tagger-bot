"""Тесты для AnalyzeEntryInteractor."""

from __future__ import annotations

from typing import Optional

import pytest

from src.domain.entities import AnalysisResult, ContentType, Entry
from src.domain.exceptions import AIServiceError, NotFoundError, ValidationError
from src.application.analyze_entry import AnalyzeEntryInteractor


class MockEntryRepository:
    """Мок-репозиторий."""

    def __init__(self, entry: Entry | None = None) -> None:
        self.entry = entry
        self.saved_entry: Optional[Entry] = None

    async def get_by_id(self, entry_id: int, user_id: int) -> Entry | None:
        return self.entry

    async def save(self, entry: Entry) -> Entry:
        self.saved_entry = entry
        return entry

    async def list_recent(self, user_id: int, limit: int = 10) -> list[Entry]:
        return []


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


class MockEmbedder:
    """Мок генератора эмбеддингов."""

    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class MockCategoryRepository:
    """Мок репозитория категорий."""

    async def get_by_id(self, category_id: int) -> Optional[str]:
        return None


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
    repository = MockEntryRepository(sample_entry)
    service = MockAnalysisService(
        result=AnalysisResult(
            summary="Python язык",
            tags=["python"],
            content_type=ContentType.ARTICLE,
        )
    )
    embedder = MockEmbedder()
    category_repository = MockCategoryRepository()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=service,
        embedder=embedder,
        category_repository=category_repository,
    )

    # When
    result = await interactor.execute(entry_id=1, user_id=123)

    # Then
    assert service.analyze_called is True
    assert result.summary == "Python язык"
    assert result.tags == ["python"]
    assert result.content_type == ContentType.ARTICLE


@pytest.mark.asyncio
async def test_analyze_entry_not_found() -> None:
    # Given
    repository = MockEntryRepository(None)
    service = MockAnalysisService()
    embedder = MockEmbedder()
    category_repository = MockCategoryRepository()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=service,
        embedder=embedder,
        category_repository=category_repository,
    )

    # When / Then
    with pytest.raises(NotFoundError, match="не найдена"):
        await interactor.execute(entry_id=999, user_id=123)


@pytest.mark.asyncio
async def test_analyze_empty_text() -> None:
    # Given
    entry = Entry(id=1, user_id=123, raw_text="   ")
    repository = MockEntryRepository(entry)
    service = MockAnalysisService()
    embedder = MockEmbedder()
    category_repository = MockCategoryRepository()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=service,
        embedder=embedder,
        category_repository=category_repository,
    )

    # When / Then
    with pytest.raises(ValidationError, match="Нет текста"):
        await interactor.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_service_error(sample_entry: Entry) -> None:
    # Given
    repository = MockEntryRepository(sample_entry)
    service = MockAnalysisService(should_raise=True)
    embedder = MockEmbedder()
    category_repository = MockCategoryRepository()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=service,
        embedder=embedder,
        category_repository=category_repository,
    )

    # When / Then
    with pytest.raises(Exception, match="Ошибка анализа"):
        await interactor.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_propagates_ai_service_error(sample_entry: Entry) -> None:
    """AIServiceError пробрасывается из interactor."""
    # Given
    repository = MockEntryRepository(sample_entry)
    category_repository = MockCategoryRepository()

    class FailingAnalysisService:
        async def analyze(self, text: str) -> AnalysisResult:
            raise AIServiceError("Не удалось разобрать ответ нейросети")

    embedder = MockEmbedder()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=FailingAnalysisService(),
        embedder=embedder,
        category_repository=category_repository,
    )

    # When / Then
    with pytest.raises(AIServiceError, match="Не удалось разобрать ответ нейросети"):
        await interactor.execute(entry_id=1, user_id=123)


@pytest.mark.asyncio
async def test_analyze_applies_result_to_entry(sample_entry: Entry) -> None:
    # Given
    repository = MockEntryRepository(sample_entry)
    result = AnalysisResult(
        summary="Краткое описание",
        tags=["тег1", "тег2", "тег3"],
        content_type=ContentType.TUTORIAL,
    )
    service = MockAnalysisService(result=result)
    embedder = MockEmbedder()
    category_repository = MockCategoryRepository()
    interactor = AnalyzeEntryInteractor(
        repository=repository,
        analysis_service=service,
        embedder=embedder,
        category_repository=category_repository,
    )

    # When
    entry = await interactor.execute(entry_id=1, user_id=123)

    # Then
    assert entry.summary == "Краткое описание"
    assert entry.tags == ["тег1", "тег2", "тег3"]
    assert entry.content_type == ContentType.TUTORIAL
