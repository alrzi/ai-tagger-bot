"""Точка входа приложения."""

import asyncio
import logging

from src.presentation.bot import create_bot, setup_di, setup_middlewares


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    bot, dp = create_bot()
    setup_di(dp)
    setup_middlewares(dp)

    logger.info("Бот запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
