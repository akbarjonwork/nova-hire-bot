# get_updates.py
import asyncio
from aiogram import Bot
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def run():
    bot = Bot(token=TOKEN)
    updates = await bot.get_updates(timeout=1, limit=100)
    for u in updates:
        print(json.dumps(u.to_python(), indent=2, ensure_ascii=False))
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run())
