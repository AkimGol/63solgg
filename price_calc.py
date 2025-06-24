import math
import requests

class CLMM:
    def __init__(self, liquidity, price_min, price_max, fee_percent=0.0):
        self.L = liquidity
        self.price_min = price_min
        self.price_max = price_max
        self.fee = fee_percent / 100  # комиссия

    def sqrt_price(self, price):
        return math.sqrt(price)

    def price_from_sqrt(self, sqrt_p):
        return sqrt_p ** 2

    def apply_fee(self, amount, direction='in'):
        if self.fee == 0:
            return amount
        if direction == 'in':
            return amount * (1 - self.fee)
        else:
            return amount / (1 - self.fee)

    def simulate_swap_y_to_x(self, price_start, price_end=None, dy_in=None):
        sqrt_start = self.sqrt_price(price_start)

        if dy_in is not None:
            sqrt_end = sqrt_start + dy_in / self.L
        elif price_end is not None:
            sqrt_end = self.sqrt_price(price_end)
        else:
            raise ValueError("Нужно указать либо 'price_end', либо 'dy_in'")

        if sqrt_end > self.sqrt_price(self.price_max):
            raise ValueError("Выход за пределы максимального диапазона")

        delta_y = self.L * (sqrt_end - sqrt_start)
        delta_x = self.L * (sqrt_end - sqrt_start) / (sqrt_end * sqrt_start)

        delta_y_with_fee = self.apply_fee(delta_y, direction='in')
        delta_x_with_fee = self.apply_fee(delta_x, direction='out')
        new_price = self.price_from_sqrt(sqrt_end)

        return {
            "dy_in": delta_y_with_fee,
            "dx_out": delta_x_with_fee,
            "new_price": new_price
        }

    def simulate_swap_x_to_y(self, price_start, price_end=None, dx_in=None):
        sqrt_start = self.sqrt_price(price_start)

        if dx_in is not None:
            numerator = dx_in * sqrt_start
            sqrt_end = sqrt_start / (1 + numerator / self.L)
        elif price_end is not None:
            sqrt_end = self.sqrt_price(price_end)
        else:
            raise ValueError("Нужно указать либо 'price_end', либо 'dx_in'")

        if sqrt_end < self.sqrt_price(self.price_min):
            raise ValueError("Выход за пределы минимального диапазона")

        delta_x = self.L * (sqrt_start - sqrt_end) / (sqrt_end * sqrt_start)
        delta_y = self.L * (sqrt_start - sqrt_end)

        delta_x_with_fee = self.apply_fee(delta_x, direction='in')
        delta_y_with_fee = self.apply_fee(delta_y, direction='out')
        new_price = self.price_from_sqrt(sqrt_end)

        return {
            "dx_in": delta_x_with_fee,
            "dy_out": delta_y_with_fee,
            "new_price": new_price
        }

# Данные из API Raydium
price_current = 143.88184789701353
mint_a = 39435.634986467  # WSOL
mint_b = 2417786.710269   # USDC
fee_rate = 0.0004         # 0.04%
price_min = 126.04
price_max = 180.50

# Приблизительная ликвидность (в CLMM она может быть распределена, но аппроксимация допустима)
L_estimate = 1000  # можно чуть увеличить для точности модели

# Создание экземпляра CLMM
pool = CLMM(
    liquidity=L_estimate,
    price_min=price_min,
    price_max=price_max,
    fee_percent=fee_rate * 100
)

# Симулируем свап 100 USDC → SOL
result = pool.simulate_swap_y_to_x(
    price_start=price_current,
    dy_in=100
)

print("=== Симуляция CLMM свапа USDC → SOL ===")
print(f"USDC вход: {result['dy_in']:.6f}")
print(f"SOL выход: {result['dx_out']:.6f}")
print(f"Новая цена после свапа: {result['new_price']:.4f} USDC/SOL")

