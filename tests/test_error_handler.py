"""Тесты для ErrorHandlerMiddleware."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from aiogram.types import CallbackQuery, Message

from src.domain.exceptions import AppError
from src.presentation.middlewares.error_handler import ErrorHandlerMiddleware


@pytest.mark.asyncio
async def test_app_error_shows_message() -> None:
    """AppError → пользователь видит текст ошибки."""
    middleware = ErrorHandlerMiddleware()

    async def failing_handler(event: object, data: dict[str, object]) -> None:
        raise AppError("Запись не найдена")

    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()

    await middleware(failing_handler, mock_message, {})

    mock_message.answer.assert_called_once_with("❌ Запись не найдена")


@pytest.mark.asyncio
async def test_unknown_error_shows_generic() -> None:
    """Exception → пользователь видит общий текст."""
    middleware = ErrorHandlerMiddleware()

    async def failing_handler(event: object, data: dict[str, object]) -> None:
        raise RuntimeError("Something went wrong")

    mock_message = AsyncMock(spec=Message)
    mock_message.answer = AsyncMock()

    await middleware(failing_handler, mock_message, {})

    mock_message.answer.assert_called_once_with("⚠️ Что-то пошло не так, мы уже чиним")


@pytest.mark.asyncio
async def test_successful_handler_passes() -> None:
    """Успешный хендлер → возвращает результат."""
    middleware = ErrorHandlerMiddleware()

    async def success_handler(event: object, data: dict[str, object]) -> str:
        return "ok"

    mock_message = AsyncMock(spec=Message)

    result = await middleware(success_handler, mock_message, {})

    assert result == "ok"


@pytest.mark.asyncio
async def test_callback_query_with_message() -> None:
    """CallbackQuery с message → вызывает message.answer()."""
    middleware = ErrorHandlerMiddleware()

    async def failing_handler(event: object, data: dict[str, object]) -> None:
        raise AppError("Ошибка")

    mock_inner_message = AsyncMock()
    mock_inner_message.answer = AsyncMock()
    mock_callback = AsyncMock(spec=CallbackQuery)
    mock_callback.message = mock_inner_message

    await middleware(failing_handler, mock_callback, {})

    mock_inner_message.answer.assert_called_once_with("❌ Ошибка")


@pytest.mark.asyncio
async def test_callback_query_without_message() -> None:
    """CallbackQuery без message → вызывает answer(show_alert=True)."""
    middleware = ErrorHandlerMiddleware()

    async def failing_handler(event: object, data: dict[str, object]) -> None:
        raise AppError("Ошибка")

    mock_callback = AsyncMock(spec=CallbackQuery)
    mock_callback.message = None
    mock_callback.answer = AsyncMock()

    await middleware(failing_handler, mock_callback, {})

    mock_callback.answer.assert_called_once_with("❌ Ошибка", show_alert=True)
