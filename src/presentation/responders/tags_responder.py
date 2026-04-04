"""Отображение списка тегов."""

from __future__ import annotations

from src.presentation.context import TelegramChatContext


class TagsResponder:
    """Отображает список тегов пользователя."""

    async def respond(self, tags: list[str], ctx: TelegramChatContext) -> None:
        """Отправить ответ пользователю."""
        if not tags:
            await ctx.send_message("У тебя пока нет сохранённых тегов.\nОни появятся автоматически после анализа записей.")
            return

        lines = [
            f"📋 Всего тегов: **{len(tags)}**",
            "",
        ]

        for tag in tags:
            lines.append(f"• `{tag}`")

        text = "\n".join(lines)

        await ctx.send_message(text, reply_markup=None)
