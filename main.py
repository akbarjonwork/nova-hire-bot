import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Import router from handlers.py (which already includes start, stop, restart)
from handlers import router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)  # <— this line registers all handlers

logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("🤖 Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
