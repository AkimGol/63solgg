from dex_pool_fetcher import DexPoolFetcher
from price_calc import CLMM

def main():
    # fetcher = DexPoolFetcher()
    # pools = fetcher.fetch_all()

    # print(f"[✓] Получено {len(pools)} пулов с TVL >= $1000")
    # for token_a, token_b, price, tvl, dex in pools[:10]:
    #     print(f"{dex.upper()}: {token_a}/{token_b} | Цена: ${price:.6f} | TVL: ${tvl:,.0f}")
    pool = CLMM(liquidity=1000000, price_min=100, price_max=120, fee_percent=0.3)

    print("=== Свап Y (USDC) → X (SOL), задан ΔY ===")
    result1 = pool.simulate_swap_y_to_x(price_start=110, dy_in=50)
    print(result1)

    print("\n=== Свап X (SOL) → Y (USDC), задан ΔX ===")
    result2 = pool.simulate_swap_x_to_y(price_start=110, dx_in=0.25)
    print(result2)

if __name__ == "__main__":
    main()
