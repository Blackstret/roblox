import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from bot.handlers import router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    bot = Bot(token=bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)

    logger.info("Starting MeowTool Bot...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
