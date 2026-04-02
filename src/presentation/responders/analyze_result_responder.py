"""Responder для отправки результата анализа."""

from __future__ import annotations

from src.domain.entities import Entry
from src.presentation.context import BotContext
from src.presentation.viewmodels.entry_viewmodel import EntryViewModel


class AnalyzeResultResponder:
    """Отправляет результат анализа пользователю."""

    async def respond(
        self,
        entry: Entry,
        ctx: BotContext,
    ) -> None:
        """Отправляет результат анализа."""
        vm = EntryViewModel.from_entity(entry)
        text = (
            f"✅ Анализ завершён!\n\n"
            f"📝 {vm.summary}\n\n"
            f"🏷 {vm.formatted_tags}"
        )
        await ctx.send_message(text)
