import aiohttp

async def get_account_info(address):
    # TronGrid
    url_TronGrid = f"https://api.trongrid.io/v1/accounts/{address}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url_TronGrid) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("data"):
                    return "activated"


    # Tronscan
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

# async def get_transactions(address):

