"""Абстракция контекста для отправки сообщений."""

from __future__ import annotations

from typing import Protocol

from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


class BotContext(Protocol):
    """Абстрактный интерфейс для отправки сообщений.

    Позволяет Responder'ам не зависеть от aiogram напрямую.
    """

    async def send_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None: ...
    async def edit_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None: ...
    async def answer_callback(self) -> None: ...

    @property
    def user_id(self) -> int: ...

    @property
    def chat_id(self) -> int: ...


class TelegramChatContext:
    """Telegram-реализация BotContext."""

    def __init__(self, event: Message | CallbackQuery) -> None:
        self._event = event

    async def send_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        if isinstance(self._event, Message):
            await self._event.answer(text, reply_markup=reply_markup)
        elif self._event.message is not None:
            await self._event.message.answer(text, reply_markup=reply_markup)

    async def edit_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        if isinstance(self._event, Message):
            await self._event.edit_text(text, reply_markup=reply_markup)
        elif self._event.message is not None:
            msg = self._event.message
            if hasattr(msg, "edit_text"):
                await msg.edit_text(text, reply_markup=reply_markup)

    async def answer_callback(self) -> None:
        if isinstance(self._event, CallbackQuery):
            await self._event.answer()

    @property
    def user_id(self) -> int:
        user = self._event.from_user
        assert user is not None
        return user.id

    @property
    def chat_id(self) -> int:
        if isinstance(self._event, Message):
            return self._event.chat.id
        assert self._event.message is not None
        return self._event.message.chat.id


class WorkerBotContext:
    """Контекст для фоновых задач (без Message)."""

    def __init__(self, bot: Bot, chat_id: int) -> None:
        self._bot = bot
        self._chat_id = chat_id

    async def send_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        await self._bot.send_message(self._chat_id, text, reply_markup=reply_markup)

    async def edit_message(
        self, text: str, reply_markup: InlineKeyboardMarkup | None = None
    ) -> None:
        # В фоновых задачах нет сообщения для редактирования
        await self.send_message(text, reply_markup)

    async def answer_callback(self) -> None:
        # В фоновых задачах нет callback'ов
        pass

    @property
    def user_id(self) -> int:
        return self._chat_id

    @property
    def chat_id(self) -> int:
        return self._chat_id
