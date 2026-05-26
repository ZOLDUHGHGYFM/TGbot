# TGbot
Бот показывает:
- баланс TRX;
- баланс USDT (TRC-20);
- последние транзакции адреса.

## Используемые технологии
- Python 3.12
- asyncio
- aiogram 3
- aiohttp
- TronScan API
- TronGrid API


## Инструкция запуска
- Клонировать репозиторий либо скачать ZIP архив и распаковать его в удобное место.
- Открыть папку проекта используя любой редактор кода (VS Code, PyCharm... )
- Открыть terminal 
- Создать виртуальное окружение `python -m venv venv`
- Установить библиотеки `pip install -r requirements.txt`
- Добавть в основной каталог проекта (TGBOT) файл .env
- Запустить файл bot.py
- проверить работоспособность бота @Tron_TestTask_bot


### Для тестирования использовались 3 аккаунта
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj (активированный аккаунт)
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdy (не существующий аккаунт)
- TYfjGNPrqPc4vGcR76uSgfAXVeSqRJGxV8 (не активированный аккаунт)