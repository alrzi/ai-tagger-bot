"""Inline-клавиатуры для бота."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def search_results_keyboard(entry_ids: list[int]) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками 'Открыть' для каждой записи."""
    buttons = [
        [InlineKeyboardButton(text=f"📖 Открыть #{entry_id}", callback_data=f"entry:{entry_id}")]
        for entry_id in entry_ids
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
