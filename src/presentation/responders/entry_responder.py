"""Responder для callback отображения полной записи."""

from __future__ import annotations

from src.domain.entities import Entry
from src.presentation.context import BotContext
from src.presentation.viewmodels.entry_viewmodel import EntryViewModel


class EntryResponder:
    """Форматирует полную запись и отправляет через BotContext."""

    async def respond(
        self,
        entry: Entry,
        ctx: BotContext,
    ) -> None:
        """Отправляет отформатированную полную запись."""
        vm = EntryViewModel.from_entity(entry)
        text = self._format(vm)
        await ctx.send_message(text)
        await ctx.answer_callback()

    def _format(self, vm: EntryViewModel) -> str:
        parts = [
            f"📝 Запись #{vm.id}",
            "",
            vm.raw_text,
            "",
            f"🏷 {vm.formatted_tags}",
        ]
        if vm.url:
            parts.append(f"🔗 {vm.url}")
        if vm.summary:
            parts.extend(["", "📋 Резюме:", vm.summary])
        return "\n".join(parts)
