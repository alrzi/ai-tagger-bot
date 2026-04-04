"""Responder для команды /search."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from src.presentation.context import BotContext
from src.presentation.viewmodels.entry_viewmodel import EntryViewModel


class SearchEntriesResponder:
    """Форматирует результаты поиска и отправляет через BotContext."""

    _SEARCH_SUMMARY_LIMIT = 200

    async def respond(
        self,
        results: list[dict[str, object]],
        ctx: BotContext,
    ) -> None:
        """Отправляет отформатированные результаты поиска."""
        if not results:
            await ctx.send_message(
                "🔍 Ничего не найдено. Попробуй другой запрос."
            )
            return

        view_models = [
            (EntryViewModel.from_dict(result), result.get("distance", 0.0), result.get("chunk_text", ""))
            for result in results
        ]
        text, entry_ids = self._format(view_models)
        keyboard = self._build_keyboard(entry_ids)
        await ctx.send_message(text, reply_markup=keyboard)

    def _format(
        self,
        results: list[tuple[EntryViewModel, object, object]],
    ) -> tuple[str, list[int]]:
        lines = [f"🔍 Найдено {len(results)} записей:"]
        entry_ids: list[int] = []
        for i, (vm, distance, chunk_text) in enumerate(results, 1):
            chunk_text = str(chunk_text)
            distance = float(distance)  # type: ignore[arg-type]
            lines.append(
                f"{i}. 🆔 {vm.id}\n"
                f"🔹 Найдено в: {chunk_text[:120]}...\n"
                f"📝 {vm.truncated_summary(self._SEARCH_SUMMARY_LIMIT)}\n"
                f"🏷 {vm.formatted_tags}"
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
