"""Responder для команды /stats."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.presentation.context import BotContext


class StatsResponder:
    """Форматирует и отправляет статистику по категориям."""

    async def respond(
        self,
        categories: UserCategories,
        stats: dict[int, int],
        ctx: BotContext,
    ) -> None:
        """Отправляет статистику."""
        total = sum(stats.values())

        lines = [f"📊 Твоя статистика ({total} записей):\n"]

        for i, name in enumerate(categories.names):
            count = stats.get(i, 0)
            emoji = self._category_emoji(i)
            bar = self._progress_bar(count, total)
            lines.append(f"{emoji} {name}: {count}")
            lines.append(f"{bar}")
            lines.append("")

        await ctx.send_message("\n".join(lines))

    @staticmethod
    def _category_emoji(position: int) -> str:
        """Возвращает эмодзи для позиции категории."""
        emojis = ["🔹", "🔸", "💎", "⭐", "🌟"]
        return emojis[position] if 0 <= position < 5 else "•"

    @staticmethod
    def _progress_bar(count: int, total: int) -> str:
        """Возвращает эмодзи-прогресс-бар с процентом."""
        if total == 0:
            return ""
        ratio = count / total
        filled = int(ratio * 10)
        bar = "🟩" * filled + "⬜" * (10 - filled)
        percent = round(ratio * 100)
        return f"{bar} {percent}%"
