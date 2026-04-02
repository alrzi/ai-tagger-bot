"""Responder для команды /search."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.domain.entities import Entry
from src.presentation.context import BotContext
from src.presentation.viewmodels.entry_viewmodel import EntryViewModel


class SearchEntriesResponder:
    """Форматирует результаты поиска и отправляет через BotContext."""

    _SEARCH_SUMMARY_LIMIT = 200

    async def respond(
        self,
        results: list[tuple[Entry, float]],
        ctx: BotContext,
    ) -> None:
        """Отправляет отформатированные результаты поиска."""
        if not results:
            await ctx.send_message(
                "🔍 Ничего не найдено. Попробуй другой запрос."
            )
            return

        view_models = [
            (EntryViewModel.from_entity(entry), similarity)
            for entry, similarity in results
        ]
        text, entry_ids = self._format(view_models)
        keyboard = self._build_keyboard(entry_ids)
        await ctx.send_message(text, reply_markup=keyboard)

    def _format(
        self,
        results: list[tuple[EntryViewModel, float]],
    ) -> tuple[str, list[int]]:
        lines = [f"🔍 Найдено {len(results)} записей:"]
        entry_ids: list[int] = []
        for i, (vm, similarity) in enumerate(results, 1):
            tags = self._format_tags(vm.tags)
            summary = self._truncate(
                vm.summary or vm.raw_text, self._SEARCH_SUMMARY_LIMIT
            )
            lines.append(
                f"{i}. 🆔 {vm.id} ({similarity:.0%})\n"
                f"📝 {summary}\n"
                f"🏷 {tags}"
            )
            if vm.id is not None:
                entry_ids.append(vm.id)
        return "\n\n".join(lines), entry_ids

    @staticmethod
    def _build_keyboard(entry_ids: list[int]) -> InlineKeyboardMarkup:
        buttons = [
            [InlineKeyboardButton(text=f"📖 Запись #{id}", callback_data=f"entry:{id}")]
            for id in entry_ids
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def _format_tags(tags: list[str]) -> str:
        return " ".join(f"#{t}" for t in tags) or "без тегов"

    @staticmethod
    def _truncate(text: str, limit: int) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
