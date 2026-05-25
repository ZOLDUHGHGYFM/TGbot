# WORKLOG

## 23.05.26

### Шаги выполнения
- через @BotFather, получил токен.
- Написал простого бота, используя `aiogram`, который отвечает "Test message" на любое сообщение.
- добавил проверку на формат и длину кошелька
- добавил проверку активации аккаунта 

### Проблемы


### Что изучил
- https://docs.aiohttp.org/en/stable/
- https://core.telegram.org/bots

### Что не сработало
- проверка существования аккаунта через create_time (не активированный аккаунт считается как не существующий)
- не удалось сделать проверку только через TronGrid


### Для проверки использовались 3 аккаунта
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj (активированный аккаунт)
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdy (не существующий аккаунт)
- TYfjGNPrqPc4vGcR76uSgfAXVeSqRJGxV8 (не активированный аккаунт)



## 24.05.26

### Шаги выполнения
- нашёл в оффициальной документации tronscan вариации get запросов 
- на основе полученной информмации написал функцию get_transactions для получения последних 5 платежей
- изменил логику get_trx_balance(), ранее он из шапки брал баланс который по умолчанию отображал trx
- добавил get_usdt_balance(), по шапке tokens перебирается вид валюты.
### Проблемы

### Что изучил
- https://github.com/tronscan/tronscan-frontend/blob/dev2019/document/api.md#4
- https://docs.tronscan.org/en/api/account
- https://docs.tronscan.org/en/api/transactions-and-transfers


### Что не сработало
- get напрямую к "tokenAbbr", забыл что сначлаа нужно использовать обращенеи к шапке раздела

### Для проверки использовались 3 аккаунта
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj (активированный аккаунт)
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdy (не существующий аккаунт)
- TYfjGNPrqPc4vGcR76uSgfAXVeSqRJGxV8 (не активированный аккаунт)






## 25.05.26

### Шаги выполнения
- Вывод 0.000000 если на аккаунте нет usdt/trx
- Добавил обработку ошибок используя try except


### Проблемы


### Что изучил
- https://www.w3schools.com/python/python_ref_exceptions.asp


### Что не сработало
- 

### Для проверки использовались 4 аккаунта
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj (активированный аккаунт)
- TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdy (не существующий аккаунт)
- TYfjGNPrqPc4vGcR76uSgfAXVeSqRJGxV8 (не активированный аккаунт)
- TCHf57z2FtZveBrWkTKwxaATv7CJkVkXmB (trx > 0, usdt = 0)