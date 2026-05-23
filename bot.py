from os import getenv
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

TOKEN = getenv("Bot_Token")
if not TOKEN:
    raise SystemExit(
        "Missing Bot_Token"
    )

router = Router()
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Отправь мне TRON-адрес (начинается с T, 34 символа), и я покажу:\n"
        "баланс TRX\n"
        "баланс USDT (TRC-20)\n"
        "последние 5 транзакций"
    )

@router.message(F.text)
async def handle_address(message: Message):
    address = message.text.strip()
    if address.startswith("T") and len(address) == 34:
        await message.answer("Valid Tron address")
    else:
        await message.answer("Invalid Tron address")

async def start_bot():
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())