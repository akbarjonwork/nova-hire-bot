# test_send.py
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
BACKLOG = os.getenv("BACKLOG_CHAT_ID")

async def run():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=BACKLOG, text="✅ NovaHire Bot connected — test message.")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run())
