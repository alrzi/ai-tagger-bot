"""Хендлер команды /status."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from dishka import FromDishka
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.ai.ollama_client import OllamaClient

router = Router()


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
