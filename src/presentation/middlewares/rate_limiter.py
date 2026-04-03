"""Middleware для ограничения частоты сообщений."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from redis.asyncio import Redis

# Lua-скрипт для атомарного INCR + EXPIRE
RATE_LIMIT_SCRIPT = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return current
"""


class RateLimitMiddleware(BaseMiddleware):
    """Ограничивает количество сообщений от пользователя."""

    def __init__(
        self,
        redis: Redis,
        max_messages: int = 10,
        window: int = 60,
    ) -> None:
        self.redis = redis
        self.max_messages = max_messages
        self.window = window

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, object]], Awaitable[object]],
        event: TelegramObject,
        data: dict[str, object],
    ) -> object:
        """Проверяет лимит сообщений."""
        if not isinstance(event, Update) or event.message is None:
            return await handler(event, data)
        
        message = event.message
        if message.from_user is None:
            return await handler(event, data)
        
        user_id = message.from_user.id
        key = f"rate_limit:{user_id}"

        # Атомарный INCR + EXPIRE через Lua
        count_str: str = await self.redis.eval(  # type: ignore[misc]
            RATE_LIMIT_SCRIPT,
            1,  # количество ключей
            key,
            self.window,
        )
        count = int(count_str)

        # Проверяем лимит
        if count > self.max_messages:
            await message.answer("⏳ Слишком много сообщений, подождите минуту")
            return None

        return await handler(event, data)
