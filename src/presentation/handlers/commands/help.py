"""Хендлер команды /help."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


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
        "/list — последние записи\n"
        "/categories — настройка категорий ромба\n"
        "/stats — статистика по категориям"
    )
