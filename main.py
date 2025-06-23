from dex_pool_fetcher import DexPoolFetcher

def main():
    fetcher = DexPoolFetcher()
    pools = fetcher.fetch_all()

    print(f"[✓] Получено {len(pools)} пулов с TVL >= $1000")
    for token_a, token_b, price, tvl, dex in pools[:10]:
        print(f"{dex.upper()}: {token_a}/{token_b} | Цена: ${price:.6f} | TVL: ${tvl:,.0f}")

if __name__ == "__main__":
    main()
