"""Хендлер команды /start."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я AI-Тегировщик 🤖\n\n"
        "Отправь мне текст или ссылку — я сохраню, "
        "проанализирую и присвою теги.\n\n"
        "Команды:\n"
        "/help — помощь\n"
        "/status — статус системы"
    )
