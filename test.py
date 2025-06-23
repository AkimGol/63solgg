import asyncio
import aiohttp
import sys
from datetime import datetime

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

JUPITER_URL = "https://quote-api.jup.ag/v6/quote"
MAX_RETRIES = 5
SLIPPAGE_BPS = 50
WSOL_AMOUNT = 3
MIN_PROFIT_LAMPORTS = 200_000
DELAY_MS = 2000

WSOL = {
    "symbol": "WSOL",
    "mint": "So11111111111111111111111111111111111111112",
    "decimals": 9
}
BONK = {
    "symbol": "BONK",
    "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "decimals": 5
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (ArbitrageBot/1.0)",
    "Accept": "application/json"
}

async def fetch_quote(session, input_mint, output_mint, amount_raw):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": str(amount_raw),
        "slippageBps": str(SLIPPAGE_BPS),
        "swapMode": "ExactIn"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with session.get(JUPITER_URL, params=params, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.json()

                elif response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 3))
                    print(f"⚠️ Rate limit (429) — пауза {retry_after} сек...")
                    await asyncio.sleep(retry_after)
                    continue

                else:
                    print(f"❌ Ответ {response.status}: {await response.text()}")
                    return None

        except aiohttp.ClientError as e:
            print(f"⚠️ Сетевая ошибка (попытка {attempt}): {e}")
            await asyncio.sleep(2 ** attempt)  # backoff: 2, 4, 8...

    print("❌ Превышено количество попыток запроса к Jupiter.")
    return None

async def check_arbitrage(session):
    amount_in = int(WSOL_AMOUNT * 10**WSOL["decimals"])
    quote1 = await fetch_quote(session, WSOL["mint"], BONK["mint"], amount_in)
    if not quote1 or "outAmount" not in quote1:
        return
    bonk_amount = int(quote1["outAmount"])

    quote2 = await fetch_quote(session, BONK["mint"], WSOL["mint"], bonk_amount)
    if not quote2 or "outAmount" not in quote2:
        return
    amount_back = int(quote2["outAmount"])
    profit = amount_back - amount_in

    if profit >= MIN_PROFIT_LAMPORTS:
        ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"\n[{ts}] ✅ PROFIT: +{profit / 1e9:.9f} WSOL")


async def main_loop():
    print("🚀 Старт опроса...")
    async with aiohttp.ClientSession() as session:
        while True:
            await check_arbitrage(session)
            await asyncio.sleep(DELAY_MS / 1000)

if __name__ == "__main__":
    asyncio.run(main_loop())
