import aiohttp
from datetime import datetime


# ==========================
# API TronScan / TronGrid
# ==========================

async def get_account_info(address):
    """
    Определяет статус аккаунта через TronScan.

    Возвращает:
    - 'activated'      : аккаунт существует и был активирован
    - 'not_activated'  : адрес корректен, но не было транзакций/активации
    - 'none-existent'  : TronScan не распознаёт адрес (не существует/не найден)
    - 'api_error'      : проблемы сети/TronScan API
    """

    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return "api_error"
                data = await response.json()

        if not isinstance(data, dict) or data.get("address") != address:
            return "адрес не распознан"

        balance = data.get("balance", 0)
        create_time = data.get("create_time")
        latest_op = data.get("latest_operation_time")
        if (balance == 0 or balance == "0") and not create_time and not latest_op:
            return "not_activated"
        return "activated"
    except aiohttp.ClientError:
        return "Ошибка подключения к API"
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"
    
        
async def get_trx_balance(address):
    """
    Возвращает баланс TRX для адреса (строка с 6 знаками после запятой).

    Источник: TronScan `/api/account` → поле `tokens`.
    """
    
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
    """
    Возвращает баланс USDT (TRC-20) для адреса (строка с 6 знаками).

    Источник: TronScan `/api/account` → поле `tokens` (tokenAbbr == 'USDT').
    """
    
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


# ==========================
# Работа с транзакциями
# ==========================


async def get_transactions(address):
    """
    Возвращает форматированный текст последних 5 транзакций (для команды “просто адрес”).

    Это “витринная” функция: готовит человекочитаемые строки и ссылки на tronscan.
    """
    
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
    
   
async def get_address_info(address: str):
    """
    Определяет “тип” адреса по данным TronScan `/api/account`.

    Возвращает:
    - 'contract' : если TronScan видит контрактные поля
    - 'exchange' : если по тегу похоже на биржу
    - 'user'     : обычный пользовательский адрес
    - строку с ошибкой: если TronScan недоступен/ответ некорректный
    """
    
    url = f"https://apilist.tronscanapi.com/api/account?address={address}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return "Ошибка подключения к TronScan API."
                data = await resp.json()
                if data.get("contractMap"):
                    return "contract"
                address_tag = data.get("addressTag", "")
                if address_tag and "exchange" in address_tag.lower():
                    return "exchange"
                return "user"
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"
    

async def fetch_transactions(address: str, limit: int = 50):
    """
    Загружает последние транзакции адреса и оставляет только успешные.

    Возвращает:
    - list[dict] успешных транзакций (может быть пустым списком)
    - строку с ошибкой при проблемах TronScan / сети
    """
    
    url = f"https://apilist.tronscanapi.com/api/transaction?address={address}&limit={limit}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return "Ошибка подключения к TronScan API."
                data = await resp.json()
                txs = data.get("data", [])
                return [tx for tx in txs if tx.get("contractRet") == "SUCCESS"]
    except aiohttp.ClientError:
        return "Ошибка подключения к TronScan API."
    except Exception as ex:
        return f"Произошла ошибка: {str(ex)}"


# ==========================
# Анализ активности
# ==========================


def _safe_int(value, default: int = 0) -> int:
    """
    Преобразует значение в int; при ошибке возвращает `default`.
    """
    
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _safe_float(value, default: float = 0.0) -> float:
    """
    Преобразует значение в float; при ошибке возвращает `default`.
    """
    
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _normalize_amount(amount_raw, token_decimal) -> float:
    """
    Нормализует “сырой” amount из TronScan с учётом decimals.
    TronScan часто отдаёт amount как строку целого числа (минимальные единицы).
    """
    amount_int = _safe_int(amount_raw, default=0)
    dec = _safe_int(token_decimal, default=6)
    if dec < 0 or dec > 30:
        dec = 6
    return amount_int / (10 ** dec)


def analyze_transactions(txs: list, address: str) -> dict:
    """
    Считает базовую статистику по транзакциям для эвристик в `/analyze`.

    Формирует:
    - входящие/исходящие счётчики и суммы
    - число уникальных контрагентов
    - число “мелких” входящих (amount < 10)
    - минимальный интервал между транзакциями (по timestamp)
    """

    addr = (address or "").strip()
    incoming = 0
    outgoing = 0
    in_sum = 0.0
    out_sum = 0.0
    small_tx_count = 0
    counterparties = set()
    timestamps = []

    for tx in txs or []:
        owner = (tx.get("ownerAddress") or "").strip()
        to = (tx.get("toAddress") or "").strip()

        token_info = tx.get("tokenInfo") or {}
        token_abbr = (token_info.get("tokenAbbr") or "").upper()
        token_decimal = token_info.get("tokenDecimal")

        amount = _normalize_amount(tx.get("amount"), token_decimal)

        ts = _safe_int(tx.get("timestamp"), default=0)
        if ts:
            timestamps.append(ts)

        if to and to == addr:
            incoming += 1
            in_sum += amount
            if owner:
                counterparties.add(owner)
            if amount > 0 and amount < 10:
                small_tx_count += 1
        elif owner and owner == addr:
            outgoing += 1
            out_sum += amount
            if to:
                counterparties.add(to)
        else:
            continue

        # Небольшая поправка: если токен неизвестен, всё равно учитываем amount.
        # Для сводки нам важнее поведение, чем точный токен.

    total = incoming + outgoing

    min_interval_sec = 10**9
    if len(timestamps) >= 2:
        timestamps.sort(reverse=True)
        for i in range(len(timestamps) - 1):
            delta_ms = timestamps[i] - timestamps[i + 1]
            if delta_ms > 0:
                min_interval_sec = min(min_interval_sec, delta_ms / 1000.0)
    if min_interval_sec == 10**9:
        min_interval_sec = 0

    return {
        "total": total,
        "incoming": incoming,
        "outgoing": outgoing,
        "in_sum": float(in_sum),
        "out_sum": float(out_sum),
        "unique_counterparties": len(counterparties),
        "small_tx_count": small_tx_count,
        "min_interval_sec": _safe_float(min_interval_sec, default=0.0),
    }


def determine_activity_type(stats: dict) -> list:
    """
    Применяет простые эвристики и возвращает список “ярлыков” активности.
    """
    
    types = []
    total = stats["total"]
    if total == 0:
        return ["Нет транзакций"]

    if total > 30 or stats["min_interval_sec"] < 10:
        types.append("Высокая активность")
    if stats["incoming"] > total * 0.8:
        types.append("Преимущественно входящие транзакции")
    elif stats["outgoing"] > total * 0.8:
        types.append("Преимущественно исходящие транзакции")

    if stats["small_tx_count"] > total * 0.5 and stats["incoming"] > total * 0.5:
        types.append("Большое количество мелких входящих переводов")
        if stats["unique_counterparties"] > 10 and stats["small_tx_count"] > 20:
            types.append("Подозрительная спам-активность")
    return types
    
    
def generate_summary(stats: dict, activity_types: list, address_type: str) -> str:
    """
    Формирует финальный человекочитаемый текст ответа для `/analyze`.
    """
    
    if stats["total"] == 0:
        return f"Анализ адреса: {address_type or 'неизвестного типа'}\nТранзакции отсутствуют или не удалось загрузить."

    lines = [
        f"Тип адреса : {address_type if address_type else 'не определён'}",
        f"Всего транзакций (успешных): {stats['total']}",
        f"Входящих: {stats['incoming']}  |  Сумма (TRX+USDT): {stats['in_sum']:.6f}",
        f"Исходящих: {stats['outgoing']}  |  Сумма (TRX+USDT): {stats['out_sum']:.6f}",
        f"Уникальных контрагентов: {stats['unique_counterparties']}",
        f"Мелких переводов (<10 ед.): {stats['small_tx_count']}",
        "",
        "Определённые типы активности:",
    ]
    if activity_types:
        for t in activity_types:
            lines.append(f"  - {t}")
    else:
        lines.append("  - Обычный пользовательский кошелёк")
    return "\n".join(lines)


async def analyze_address(address):
    """
    Основной обработчик анализа адреса для команды `/analyze`.

    Поток:
    - определить статус аккаунта (не существует/не активирован/ок)
    - попытаться определить тип адреса (contract/exchange/user)
    - загрузить последние транзакции
    - собрать статистику и применить эвристики
    - вернуть краткую текстовую сводку
    """
    
    status = await get_account_info(address)
    if status == "none-existent":
        return f"Адрес {address} не существует или не распознан TronScan."
    if status == "not_activated":
        return f"Адрес {address} корректен, но кошелёк не активирован (транзакций нет)."
    if status == "api_error":
        return "Не удалось подключиться к TronScan API. Повторите позже."

    addr_type = await get_address_info(address)
    if isinstance(addr_type, str) and ("Ошибка подключения" in addr_type or "Произошла ошибка" in addr_type):
        addr_type = None
    txs = await fetch_transactions(address, limit=50)
    if isinstance(txs, str):
        return f"Не удалось загрузить транзакции для адреса {address}.\n{txs}"

    stats = analyze_transactions(txs, address)
    activity = determine_activity_type(stats)
    addr_type_str = addr_type if addr_type is not None else "не определён"
    summary = generate_summary(stats, activity, addr_type_str)
    return summary


# ==========================
# Вспомогательные функции
# ==========================


def format_amount(amount_str, decimal):
    """
    Форматирует целое значение (строка/число) с учётом decimals.
    """
    
    amount = int(amount_str)
    return amount / (10 ** decimal)