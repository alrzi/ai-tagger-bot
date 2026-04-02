"""Тесты для OllamaEntryAnalysisService.

Проверяем логику маппинга DTO → доменный объект.
Парсинг JSON делегирован клиенту через generate_structured().
"""

from __future__ import annotations

from typing import TypeVar

import pytest
from pydantic import BaseModel

from src.domain.entities import AnalysisResult, ContentType
from src.domain.exceptions import AIServiceError
from src.infrastructure.ai.analysis import OllamaEntryAnalysisService
from src.infrastructure.ai.schemas import AIAnalysisDTO

T = TypeVar("T", bound=BaseModel)


class MockAIClient:
    """Мок ИИ-клиента с поддержкой generate_structured."""

    def __init__(
        self,
        dto: AIAnalysisDTO | None = None,
        should_raise: bool = False,
    ) -> None:
        self.dto = dto or AIAnalysisDTO(
            summary="Тест",
            tags=["тег"],
            type="article",
        )
        self.should_raise = should_raise
        self.generate_structured_called = False
        self.last_prompt: str | None = None

    async def generate(self, prompt: str) -> str:
        return "{}"

    async def generate_structured(
        self, prompt: str, schema: type[T], system: str | None = None
    ) -> T:
        self.generate_structured_called = True
        self.last_prompt = prompt
        if self.should_raise:
            raise ValueError("Модель вернула ошибку")
        return self.dto  # type: ignore[return-value]


@pytest.mark.asyncio
async def test_analyze_valid_response() -> None:
    # Given
    client = MockAIClient(AIAnalysisDTO(
        summary="Python язык программирования",
        tags=["python", "programming"],
        type="article",
    ))
    service = OllamaEntryAnalysisService(ai_client=client)

    # When
    result = await service.analyze("Текст для анализа")

    # Then
    assert client.generate_structured_called is True
    assert isinstance(result, AnalysisResult)
    assert result.summary == "Python язык программирования"
    assert result.tags == ["python", "programming"]
    assert result.content_type == ContentType.ARTICLE


@pytest.mark.asyncio
async def test_analyze_summary_as_list() -> None:
    # Given — DTO с summary как список (валидатор склеит)
    client = MockAIClient(AIAnalysisDTO(
        summary=["Первое.", "Второе."],
        tags=["тег"],
        type="note",
    ))
    service = OllamaEntryAnalysisService(ai_client=client)

    # When
    result = await service.analyze("Текст")

    # Then
    assert result.summary == "Первое. Второе."
    assert result.content_type == ContentType.NOTE


@pytest.mark.asyncio
async def test_analyze_tags_as_string() -> None:
    # Given — DTO с tags как строку (валидатор разделит)
    client = MockAIClient(AIAnalysisDTO(
        summary="Тест",
        tags="python, code, tutorial",
        type="tutorial",
    ))
    service = OllamaEntryAnalysisService(ai_client=client)

    # When
    result = await service.analyze("Текст")

    # Then
    assert result.tags == ["python", "code", "tutorial"]


@pytest.mark.asyncio
async def test_analyze_unknown_content_type() -> None:
    # Given — неизвестный type
    client = MockAIClient(AIAnalysisDTO(
        summary="Тест",
        tags=["тег"],
        type="podcast",
    ))
    service = OllamaEntryAnalysisService(ai_client=client)

    # When
    result = await service.analyze("Текст")

    # Then
    assert result.content_type == ContentType.UNKNOWN


@pytest.mark.asyncio
async def test_analyze_client_error() -> None:
    # Given — клиент выбрасывает ошибку
    client = MockAIClient(should_raise=True)
    service = OllamaEntryAnalysisService(ai_client=client)

    # When / Then
    with pytest.raises(AIServiceError, match="Не удалось разобрать"):
        await service.analyze("Текст")


@pytest.mark.asyncio
async def test_analyze_truncates_long_text() -> None:
    # Given — длинный текст
    client = MockAIClient()
    service = OllamaEntryAnalysisService(ai_client=client)

    # When
    await service.analyze("A" * 5000)

    # Then — промпт содержит не более 3000 символов контента
    assert client.last_prompt is not None
    assert "A" * 3000 in client.last_prompt
    assert "A" * 3001 not in client.last_prompt
