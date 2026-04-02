"""Тесты для фоновых задач Taskiq."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.domain.entities import ContentType, Entry
from src.domain.exceptions import AIServiceError, NotFoundError, ValidationError
from src.tasks.worker import _analyze_entry_logic


@pytest.fixture
def sample_entry() -> Entry:
    return Entry(
        id=1,
        user_id=123,
        raw_text="Python — язык программирования",
        summary="Python язык",
        tags=["python"],
        content_type=ContentType.ARTICLE,
    )


@pytest.mark.asyncio
async def test_analyze_entry_task_success(sample_entry: Entry) -> None:
    """Таска вызывает interactor и возвращает результат."""
    mock_interactor = AsyncMock()
    mock_interactor.execute.return_value = sample_entry

    result = await _analyze_entry_logic(
        entry_id=1,
        user_id=123,
        interactor=mock_interactor,
    )

    assert isinstance(result, Entry)
    assert result.id == 1
    assert result.tags == ["python"]
    assert result.summary == "Python язык"
    mock_interactor.execute.assert_called_once_with(1, 123)


@pytest.mark.asyncio
async def test_analyze_entry_task_not_found() -> None:
    """NotFoundError → cancelled (не retry)."""
    mock_interactor = AsyncMock()
    mock_interactor.execute.side_effect = NotFoundError("Запись не найдена")

    result = await _analyze_entry_logic(
        entry_id=999,
        user_id=123,
        interactor=mock_interactor,
    )

    assert isinstance(result, dict)
    assert result["status"] == "cancelled"
    assert "Запись не найдена" in result["reason"]


@pytest.mark.asyncio
async def test_analyze_entry_task_validation_error() -> None:
    """ValidationError → cancelled (не retry)."""
    mock_interactor = AsyncMock()
    mock_interactor.execute.side_effect = ValidationError("Нет текста для анализа")

    result = await _analyze_entry_logic(
        entry_id=1,
        user_id=123,
        interactor=mock_interactor,
    )

    assert isinstance(result, dict)
    assert result["status"] == "cancelled"
    assert "Нет текста для анализа" in result["reason"]


@pytest.mark.asyncio
async def test_analyze_entry_task_ai_error() -> None:
    """AIServiceError → пробрасывается (retry)."""
    mock_interactor = AsyncMock()
    mock_interactor.execute.side_effect = AIServiceError("Ошибка ИИ")

    with pytest.raises(AIServiceError, match="Ошибка ИИ"):
        await _analyze_entry_logic(
            entry_id=1,
            user_id=123,
            interactor=mock_interactor,
        )
