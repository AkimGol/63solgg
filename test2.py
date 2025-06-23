import asyncio
from solana.rpc.async_api import AsyncClient
from solana.publickey import PublicKey
from raydium_layouts import LIQUIDITY_STATE_LAYOUT_V4, CLMM_POOL_LAYOUT
from meteora.dlmm import DLMM

class DEXParser:
    def __init__(self, rpc_url: str):
        self.client = AsyncClient(rpc_url)

    async def get_amm_reserves(self, pool_address: str):
        info = await self.client.get_account_info(PublicKey(pool_address))
        s = LIQUIDITY_STATE_LAYOUT_V4.decode(info.value.data)
        return s.baseReserve, s.quoteReserve

    async def get_clmm_state(self, pool_address: str):
        info = await self.client.get_account_info(PublicKey(pool_address))
        s = CLMM_POOL_LAYOUT.decode(info.value.data)
        return s.sqrt_price, s.liquidity

    async def get_dlmm_state(self, pool_address: str):
        dlmm = await DLMM.create(self.client, PublicKey(pool_address))
        active = await dlmm.get_active_bin()
        return active.binId, dlmm.fromPricePerLamport(active.price)

    async def close(self):
        await self.client.close()

async def main():
    p = DEXParser("https://api.mainnet-beta.solana.com")
    print(await p.get_amm_reserves("Raydium_AMM_POOL_ADDRESS"))
    print(await p.get_clmm_state("Raydium_CLMM_POOL_ADDRESS"))
    print(await p.get_dlmm_state("Meteora_DLMM_POOL_ADDRESS"))
    await p.close()

if __name__ == "__main__":
    asyncio.run(main())
