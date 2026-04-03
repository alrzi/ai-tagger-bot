"""Middleware для объединения сообщений пользователя."""

from __future__ import annotations

from asyncio import sleep
from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from redis.asyncio import Redis


class DebounceMiddleware(BaseMiddleware):
    """Объединяет быстрые сообщения пользователя в один запрос."""

    def __init__(
        self,
        redis: Redis,
        delay: float = 2.0,
    ) -> None:
        self.redis = redis
        self.delay = delay

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Дебаунсит сообщения пользователя."""
        if not isinstance(event, Update) or event.message is None:
            return await handler(event, data)
        
        message = event.message
        if message.from_user is None or message.text is None:
            return await handler(event, data)
        
        user_id = message.from_user.id
        key = f"debounce:{user_id}"

        # Сохраняем сообщение в Redis
        await self.redis.set(key, message.text, ex=int(self.delay) + 5)

        # Ждём задержку
        await sleep(self.delay)

        # Проверяем актуальность сообщения
        current = await self.redis.get(key)
        if current is None or current.decode() != message.text:
            # Сообщение устарело, пропускаем
            return None

        # Удаляем ключ и обрабатываем
        await self.redis.delete(key)
        return await handler(event, data)
