import aiohttp
from datetime import datetime


# ==========================
# API TronScan / TronGrid
# ==========================

async def get_account_info(address):
    # TronGrid
    url_TronGrid = f"https://api.trongrid.io/v1/accounts/{address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_TronGrid) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data"):
                        return "activated"
                else: 
                    return "Не удалсь подключить к TronGrid API"
    except aiohttp.ClientError:
        return "Ошибка подключения к TronGrid API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"


    # TronScan
    url_TronScan = f"https://apilist.tronscanapi.com/api/account?address={address}" 
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_TronScan) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("address") == address:
                        if data.get("balance", 0) == 0 and not data.get("create_time"):
                            return "not_activated"
                        else:
                            return "activated"
                return "Не удалсь подключить к TronScan API"
        return "none-existent"
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"
    
        
async def get_trx_balance(address):
    balance_url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(balance_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for token in data.get("tokens", []):
                        if token.get("tokenAbbr") == "trx":
                            if token.get("balance") != "0":
                                balance_raw = token.get("balance", "0")
                                balance_decimal = token.get("tokenDecimal", 6)
                                balance_formatted = format_amount(balance_raw, balance_decimal)
                                return f"{balance_formatted:.6f}"
                            return "0.000000"
                else:
                    return "Ошибка подключения к TronScan API."
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"
    
                
async def get_usdt_balance(address):
    balance_url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(balance_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for token in data.get("tokens", []):
                        if token.get("tokenAbbr") == "USDT":
                            if token.get("balance") != "0":
                                balance_raw = token.get("balance", "0")
                                balance_decimal = token.get("tokenDecimal", 6)
                                balance_formatted = format_amount(balance_raw, balance_decimal)
                                return f"{balance_formatted:.6f}"
                            return "0.000000"
                    else:
                        return "0.000000"
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"


async def is_contract():
    # Проверить, является ли адрес контрактом (на основе данных из TronScan)
    pass


# ==========================
# Работа с транзакциями
# ==========================


async def get_transactions(address):
    url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=5"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    transactions = data.get("data", [])
                    result_lines = []
                    for transaction in transactions:
                        transaction_hash = transaction.get("hash")
                        timestamp = transaction.get("timestamp")
                        dt_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                        sender = transaction.get("ownerAddress", "Нет информации")
                        receiver = transaction.get("toAddress", "Нет информации")
                        amount_raw = transaction.get("amount", "Нет информации")
                        token_info = transaction.get("tokenInfo", "Нет информации")
                        token_Abbr = token_info.get("tokenAbbr", "Нет информации")
                        token_decimal = token_info.get("tokenDecimal", "Нет информации")
                        amount_formatted = f"{format_amount(amount_raw, token_decimal):.6f}"
                        status = "Успешно" if transaction.get("contractRet") == "SUCCESS" else "Неудачно"

                        result_lines.append(
                            f"{dt_str}\n"
                            f"Сумма: {amount_formatted} Токен: {token_Abbr.upper()}\n"
                            f"Отправитель: {sender} -> Получатель: {receiver}\n"
                            f"Статус: {status}\n"
                            f"https://tronscan.org/#/transaction/{transaction_hash}\n"
                        )
                    return "\n".join(result_lines)
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"
    
    
def parse_transaction():
    # На основе данных о транзакциях определить тип транзакции (входящая, исходящая, контракт)
    pass
    

async def fetch_recent_transactions():
    # Получить последние транзакции для адреса
    pass


# ==========================
# Анализ активности
# ==========================


def determine_activity_type():
    # На основе анализа транзакций и типов активности определить, чем занимается адрес (трейдинг, стейкинг, взаимодействия с DeFi)
    pass
    
    
def generate_analysis_summary():
    # На основе анализа транзакций и типов активности сформировать краткий отчёт для пользователя
    pass


async def analyze_address(address):
    # Получить последние транзакции
    # Проанализировать типы транзакций (входящие, исходящие, контракты)
    # Определить активность (трейдинг, стейкинг, взаимодействия с DeFi)
    # Сформировать краткий отчёт для пользователя
    pass


# ==========================
# Вспомогательные функции
# ==========================

def format_amount(amount_str, decimal):
    amount = int(amount_str)
    return amount / (10 ** decimal)