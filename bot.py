from os import getenv
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

TOKEN = getenv("Bot_Token")
if not TOKEN:
    raise SystemExit(
        "Missing Bot_Token"
    )

router = Router()
@router.message()
async def write_message(message: Message):
    await message.answer("Test message")


async def start_bot():
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())