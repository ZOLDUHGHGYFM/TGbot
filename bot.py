from os import getenv
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

from TronApi import get_account_info, get_trx_balance, get_transactions

load_dotenv(dotenv_path=".env")

TOKEN = getenv("Bot_Token")
if not TOKEN:
    raise SystemExit("Missing Bot_Token")

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
        await message.answer("Адрес введён верно, ищу информацию")
        status = await get_account_info(address)
        
        if status == "activated":
            trx_balance = await get_trx_balance(address) 
            await message.answer(f"Баланс TRX: {trx_balance}")
            transactions = await get_transactions(address)
            await message.answer(f"Последние 5 транзакций для адреса {address}:\n{transactions}")
            
        elif status == "not_activated":
            await message.answer("Адрес корректен, но кошелёк не активирован (нет транзакций).")
            
        else:
            await message.answer("Аккаунт с таким адресом не существует.")
            
    else:
        await message.answer("Отправлен не корректный TRON-адрес.")

async def start_bot():
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())