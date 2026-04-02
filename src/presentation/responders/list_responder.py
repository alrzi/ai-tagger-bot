"""Responder для команды /list."""

from __future__ import annotations

from src.domain.entities import Entry
from src.presentation.context import BotContext
from src.presentation.viewmodels.entry_viewmodel import EntryViewModel


class ListEntriesResponder:
    """Форматирует список записей и отправляет через BotContext."""

    _SUMMARY_LIMIT = 100

    async def respond(
        self,
        entries: list[Entry],
        ctx: BotContext,
    ) -> None:
        """Отправляет отформатированный список записей."""
        if not entries:
            await ctx.send_message(
                "📋 У тебя пока нет записей.\n"
                "Отправь текст или ссылку — я сохраню!"
            )
            return

        view_models = [EntryViewModel.from_entity(e) for e in entries]
        text = self._format(view_models)
        await ctx.send_message(text)

    def _format(self, entries: list[EntryViewModel]) -> str:
        lines = [f"📋 Последние {len(entries)} записей:"]
        for vm in entries:
            tags = self._format_tags(vm.tags)
            summary = self._truncate(
                vm.summary or vm.raw_text, self._SUMMARY_LIMIT
            )
            lines.append(f"🆔 {vm.id}\n📝 {summary}\n🏷 {tags}")
        return "\n\n".join(lines)

    @staticmethod
    def _format_tags(tags: list[str]) -> str:
        return " ".join(f"#{t}" for t in tags) or "без тегов"

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
