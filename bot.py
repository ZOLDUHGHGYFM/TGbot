from os import getenv
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

from TronApi import (
    get_account_info,
    get_trx_balance,
    get_usdt_balance,
    get_transactions,
    analyze_address
)

load_dotenv(dotenv_path=".env")

TOKEN = getenv("Bot_Token")
if not TOKEN:
    raise SystemExit("Missing Bot_Token")

router = Router()
@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Показывает справку и примеры использования бота.
    """
    
    await message.answer(
        "Отправь TRON-адрес (начинается с T, 34 символа), и я покажу:\n"
        "- баланс TRX\n"
        "- баланс USDT (TRC-20)\n"
        "- последние 5 транзакций\n\n"
        "Команда /analyze ADDRESS — анализ последних транзакций и типа активности."
    )


def _is_tron_address(text: str) -> bool:
    """
    Минимальная валидация TRON-адреса.
    """
    
    address = text.strip()
    return address.startswith("T") and len(address) == 34


@router.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """
    Обрабатывает `/analyze ADDRESS` и возвращает сводку активности адреса.
    """
    
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not _is_tron_address(parts[1]):
        await message.answer(
            "Использование: /analyze ADDRESS\n"
            "Пример: /analyze TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
        )
        return

    address = parts[1].strip()
    await message.answer("Анализирую адрес, подождите…")
    summary = await analyze_address(address)
    await message.answer(summary)


@router.message(F.text & ~F.text.startswith("/"))
async def handle_address(message: Message):
    """
    Обрабатывает отправленный адрес без команды: баланс и последние 5 транзакций.
    """
    
    if message.text is None:
        await message.answer("Пожалуйста, отправьте текст с адресом.")
        return
    address = message.text.strip()
    if address.startswith("T") and len(address) == 34:
        await message.answer("Адрес введён верно, ищу информацию")
        status = await get_account_info(address)
        
        if status == "activated":
            trx_balance = await get_trx_balance(address)
            await message.answer(f"Баланс TRX: {trx_balance}")
            usdt_balance = await get_usdt_balance(address)  
            await message.answer(f"Баланс USDT: {usdt_balance}")
            transactions = await get_transactions(address)
            await message.answer(f"Последние 5 транзакций для адреса {address}:\n{transactions}")
            
        elif status == "not_activated":
            await message.answer("Адрес корректен, но кошелёк не активирован (нет транзакций).")
            
        else:
            await message.answer("Аккаунт с таким адресом не существует.")
            
    else:
        await message.answer("Отправлен не корректный TRON-адрес.")

async def start_bot():
    """
    Создаёт бота и запускает long-polling.
    """
    
    bot = Bot(token=TOKEN) # type: ignore

    dp = Dispatcher()
    dp.include_router(router)

    print("Bot is running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())