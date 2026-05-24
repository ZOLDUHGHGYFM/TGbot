import aiohttp
from datetime import datetime


async def get_account_info(address):
    # TronGrid
    url_TronGrid = f"https://api.trongrid.io/v1/accounts/{address}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url_TronGrid) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("data"):
                    return "activated"


    # TronScan
    url_TronScan = f"https://apilist.tronscanapi.com/api/account?address={address}"    
    async with aiohttp.ClientSession() as session:
        async with session.get(url_TronScan) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("address") == address:
                    if data.get("balance", 0) == 0 and not data.get("create_time"):
                        return "not_activated"
                    else:
                        return "activated"
    return "none-existent"
        
async def get_trx_balance(address):
    balance_url = f"https://apilist.tronscanapi.com/api/account?address={address}"

    async with aiohttp.ClientSession() as session:
        async with session.get(balance_url) as response:
            if response.status == 200:
                data = await response.json()
                trx_balance = data.get("balance", 0) / 1_000_000
                return trx_balance
            else:
                print(f"Произошла ошибка: {response.status}")
                return None
            
# async def get_usdt_balance(address):


async def get_transactions(address):
    url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit=5"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                transactions = data.get("data", [])
                if not transactions:
                    return "Нет транзакций."
                
                result_lines = []
                for transaction in transactions:
                    transaction_hash = transaction.get("hash")
                    timestamp = transaction.get("timestamp")
                    dt_str = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # dict.get(key, default)
                    sender = transaction.get("ownerAddress", "Нет информации")
                    receiver = transaction.get("toAddress", "Нет информации")
                    amount_raw = transaction.get("amount", "Нет информации")
                    token_info = transaction.get("tokenInfo", "Нет информации") # 
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
            else:
                return "Ошибка при получении информации."
            
            
def format_amount(amount_str, decimal):
    amount = int(amount_str)
    return amount / (10 ** decimal)