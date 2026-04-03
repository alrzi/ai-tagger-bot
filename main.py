"""Точка входа приложения."""

import asyncio
import logging

from redis.asyncio import Redis

from config.settings import settings
from src.presentation.bot import create_bot, setup_di, setup_middlewares


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    bot, dp = create_bot()
    setup_di(dp)
    
    # Создаём Redis для middleware
    redis = Redis.from_url(settings.redis_url)
    setup_middlewares(dp, redis)

    logger.info("Бот запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
