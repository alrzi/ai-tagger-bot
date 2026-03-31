"""Хендлер команды /start и /help."""

from aiogram import Router
from aiogram.filters import CommandStart, Command
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


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📖 Как пользоваться:\n\n"
        "1. Перешли мне пост или отправь ссылку\n"
        "2. Я извлеку текст, напишу резюме и теги\n"
        "3. Потом можешь искать по смыслу: /search <запрос>\n\n"
        "Команды:\n"
        "/start — перезапуск\n"
        "/status — проверить подключение к БД и ИИ\n"
        "/list — последние записи"
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer(
        "✅ Бот работает!\n"
        "⏳ Проверка БД и Ollama будет добавлена на следующем шаге."
    )
