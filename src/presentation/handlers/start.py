"""Хендлер команды /start и /help."""

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dishka import FromDishka
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.ai.ollama_client import OllamaClient

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
async def cmd_status(
    message: Message,
    session: FromDishka[AsyncSession],
    ollama: FromDishka[OllamaClient],
) -> None:
    # Проверяем подключение к БД
    db_status = "❌ Не подключена"
    try:
        await session.execute(text("SELECT 1"))
        db_status = "✅ Подключена"
    except Exception as e:
        db_status = f"❌ Ошибка: {e}"

    # Проверяем подключение к Ollama
    ollama_status = "❌ Не подключён"
    try:
        if await ollama.health_check():
            models = await ollama.list_models()
            ollama_status = f"✅ Доступен (модели: {', '.join(models[:3])})"
        else:
            ollama_status = "❌ Недоступен"
    except Exception as e:
        ollama_status = f"❌ Ошибка: {e}"

    await message.answer(
        f"✅ Бот работает!\n"
        f"🗄 База данных: {db_status}\n"
        f"🤖 Ollama: {ollama_status}"
    )
