import aiohttp
from datetime import datetime


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


def parse_transaction(transaction, address):
    token_info = transaction.get("tokenInfo") or {}
    token_abbr = (token_info.get("tokenAbbr") or "trx").lower()
    token_decimal = token_info.get("tokenDecimal", 6)
    amount_raw = transaction.get("amount", 0)
    try:
        amount = format_amount(amount_raw, token_decimal)
    except (TypeError, ValueError):
        amount = 0.0

    sender = transaction.get("ownerAddress", "")
    receiver = transaction.get("toAddress", "")
    if sender == address:
        direction = "out"
    elif receiver == address:
        direction = "in"
    else:
        direction = "other"

    timestamp = transaction.get("timestamp", 0)
    return {
        "hash": transaction.get("hash"),
        "timestamp": timestamp,
        "direction": direction,
        "token": token_abbr,
        "amount": amount,
        "success": transaction.get("contractRet") == "SUCCESS",
        "sender": sender,
        "receiver": receiver,
    }


async def fetch_recent_transactions(address, limit=20):
    url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit={limit}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None, "Ошибка подключения к TronScan API."
                data = await response.json()
                transactions = data.get("data", [])
                return [parse_transaction(tx, address) for tx in transactions], None
    except aiohttp.ClientError:
        return None, "Ошибка подключения к TronScan API."
    except Exception as ex:
        return None, f"Произошла ошибка: {str(ex)}"


def determine_activity_type(transactions, address):
    successful = [tx for tx in transactions if tx["success"] and tx["direction"] in ("in", "out")]
    if not successful:
        return "неактивный", {}

    incoming = [tx for tx in successful if tx["direction"] == "in"]
    outgoing = [tx for tx in successful if tx["direction"] == "out"]

    usdt_in = sum(tx["amount"] for tx in incoming if tx["token"] == "usdt")
    usdt_out = sum(tx["amount"] for tx in outgoing if tx["token"] == "usdt")
    trx_in = sum(tx["amount"] for tx in incoming if tx["token"] == "trx")
    trx_out = sum(tx["amount"] for tx in outgoing if tx["token"] == "trx")

    in_count = len(incoming)
    out_count = len(outgoing)
    total = in_count + out_count

    if usdt_in + usdt_out > trx_in + trx_out and (usdt_in + usdt_out) > 0:
        token_focus = "USDT"
    elif trx_in + trx_out > 0:
        token_focus = "TRX"
    else:
        token_focus = "смешанные токены"

    if total >= 15 and in_count > 0 and out_count > 0:
        ratio = min(in_count, out_count) / max(in_count, out_count)
        if ratio >= 0.4:
            activity_type = "сервисный / биржевой кошелёк"
        elif in_count > out_count * 2:
            activity_type = "получатель средств"
        elif out_count > in_count * 2:
            activity_type = "отправитель средств"
        else:
            activity_type = "высокая смешанная активность"
    elif in_count > out_count * 2:
        activity_type = "получатель средств"
    elif out_count > in_count * 2:
        activity_type = "отправитель средств"
    elif total <= 2:
        activity_type = "редкая активность (хранение)"
    elif usdt_in + usdt_out > trx_in + trx_out:
        activity_type = "активность в USDT"
    else:
        activity_type = "обычный пользовательский кошелёк"

    stats = {
        "sample_size": len(transactions),
        "successful_count": len(successful),
        "in_count": in_count,
        "out_count": out_count,
        "usdt_in": usdt_in,
        "usdt_out": usdt_out,
        "trx_in": trx_in,
        "trx_out": trx_out,
        "token_focus": token_focus,
    }
    return activity_type, stats


def generate_analysis_summary(address, activity_type, stats, transactions):
    timestamps = [tx["timestamp"] for tx in transactions if tx.get("timestamp")]
    period = ""
    if timestamps:
        oldest = datetime.fromtimestamp(min(timestamps) / 1000).strftime("%Y-%m-%d")
        newest = datetime.fromtimestamp(max(timestamps) / 1000).strftime("%Y-%m-%d")
        period = f"Период выборки: {oldest} — {newest}\n"

    lines = [
        f"Анализ адреса {address}",
        "",
        f"Тип активности: {activity_type}",
        f"Основной токен в операциях: {stats.get('token_focus', '—')}",
        period.rstrip(),
        f"Проанализировано транзакций: {stats.get('sample_size', 0)} "
        f"(успешных: {stats.get('successful_count', 0)})",
        f"Входящих: {stats.get('in_count', 0)}, исходящих: {stats.get('out_count', 0)}",
    ]

    if stats.get("usdt_in") or stats.get("usdt_out"):
        lines.append(
            f"USDT: получено ~{stats['usdt_in']:.2f}, отправлено ~{stats['usdt_out']:.2f}"
        )
    if stats.get("trx_in") or stats.get("trx_out"):
        lines.append(
            f"TRX: получено ~{stats['trx_in']:.2f}, отправлено ~{stats['trx_out']:.2f}"
        )

    in_c = stats.get("in_count", 0)
    out_c = stats.get("out_count", 0)
    if in_c > out_c:
        brief = "Адрес чаще принимает переводы, чем отправляет."
    elif out_c > in_c:
        brief = "Адрес чаще отправляет средства, чем получает."
    elif in_c and out_c:
        brief = "Входящие и исходящие переводы примерно сбалансированы."
    else:
        brief = "За выбранный период заметной активности не обнаружено."

    lines.extend(["", "Кратко:", brief])
    return "\n".join(line for line in lines if line is not None)


async def analyze_address(address):
    status = await get_account_info(address)
    if status == "not_activated":
        return "Адрес корректен, но кошелёк не активирован — анализировать нечего."
    if status != "activated":
        return "Аккаунт с таким адресом не существует или недоступен для анализа."

    transactions, error = await fetch_recent_transactions(address, limit=20)
    if error:
        return error
    if not transactions:
        return (
            f"Адрес {address} активирован, но за последнее время транзакций не найдено.\n"
            "Тип активности: неактивный."
        )

    activity_type, stats = determine_activity_type(transactions, address)
    return generate_analysis_summary(address, activity_type, stats, transactions)


def format_amount(amount_str, decimal):
    amount = int(amount_str)
    return amount / (10 ** decimal)