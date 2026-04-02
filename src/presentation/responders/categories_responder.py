"""Responder для команды /categories."""

from __future__ import annotations

from src.domain.entities import UserCategories
from src.presentation.context import BotContext


class CategoriesResponder:
    """Форматирует и отправляет категории пользователя."""

    async def respond(
        self,
        categories: UserCategories,
        ctx: BotContext,
    ) -> None:
        """Отправляет список категорий."""
        lines = ["📊 Твои категории для ромба:\n"]
        for i, name in enumerate(categories.names, 1):
            emoji = self._category_emoji(i)
            lines.append(f"{emoji} {i}. {name}")

        lines.append("\nИзменить: /categories set Кат1 Кат2 Кат3 Кат4 Кат5")
        lines.append("Сбросить: /categories reset")

        await ctx.send_message("\n".join(lines))

    async def respond_updated(
        self,
        categories: UserCategories,
        ctx: BotContext,
    ) -> None:
        """Отправляет подтверждение обновления."""
        lines = ["✅ Категории обновлены!\n"]
        for i, name in enumerate(categories.names, 1):
            emoji = self._category_emoji(i)
            lines.append(f"{emoji} {i}. {name}")

        await ctx.send_message("\n".join(lines))

    @staticmethod
    def _category_emoji(position: int) -> str:
        """Возвращает эмодзи для позиции категории."""
        emojis = ["🔹", "🔸", "💎", "⭐", "🌟"]
        return emojis[position - 1] if 1 <= position <= 5 else "•"
