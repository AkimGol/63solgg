import requests
from typing import List, Tuple

class DexPoolFetcher:
    def __init__(self):
        self.api_url = "https://api.dexscreener.com/latest/dex/search?q=solana"
        self.min_tvl_usd = 1000  # фильтр по минимальной ликвидности

    def fetch_all(self) -> List[Tuple[str, str, float, float, str]]:
        """
        Получает данные всех DEX-пар через DexScreener (только Solana).
        Возвращает список кортежей: (tokenA, tokenB, price, tvl, dex_name)
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"[!] Ошибка при запросе к DexScreener: {e}")
            return []

        raw_pairs = data.get("pairs", [])
        parsed = []

        for item in raw_pairs:
            try:
                token_a = item["baseToken"]["symbol"]
                token_b = item["quoteToken"]["symbol"]
                price = float(item.get("priceUsd", 0))
                tvl = float(item.get("liquidity", {}).get("usd", 0))
                dex = item.get("dexId", "unknown")

                if tvl >= self.min_tvl_usd and price > 0:
                    parsed.append((token_a, token_b, price, tvl, dex))
            except Exception:
                continue

        return parsed
