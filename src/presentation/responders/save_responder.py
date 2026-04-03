"""Responder для сохранения записи."""

from __future__ import annotations

from src.domain.entities import Entry
from src.presentation.context import BotContext


class SaveEntryResponder:
    """Форматирует ответ после сохранения записи."""

    async def respond(
        self,
        entry: Entry,
        ctx: BotContext,
    ) -> None:
        """Отправляет подтверждение сохранения."""
        text = "✅ Сохранено!\n⏳ Анализирую через ИИ..."
        await ctx.send_message(text)
