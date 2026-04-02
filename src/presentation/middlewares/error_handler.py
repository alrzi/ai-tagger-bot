"""Middleware для глобальной обработки ошибок."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.domain.exceptions import AppError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """Перехватывает исключения из хендлеров и отвечает пользователю."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except AppError as exc:
            # Пользовательские ошибки — без трейсбека
            logger.info("AppError: %s", exc.message)
            await self._reply(event, f"❌ {exc.message}")
        except Exception:
            # Неизвестная ошибка — полный трейсбек
            logger.exception("Unexpected error in handler")
            await self._reply(event, "⚠️ Что-то пошло не так, мы уже чиним")

    @staticmethod
    async def _reply(event: TelegramObject, text: str) -> None:
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery) and event.message:
            await event.message.answer(text)
        elif isinstance(event, CallbackQuery):
            await event.answer(text, show_alert=True)
