from tokens_abi import USDT_ABI,DAI_ABI,USDC_ABI,ABI_ETH
STABLECOINS = ['USDC', 'USDT', 'DAI']
TOKEN_CONFIG = {
    'USDC': {
        'abi': USDC_ABI,
        'address': 0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8,
        'decimals': 6,
        'approve_address': 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
        'pool_id': 1  # pool_id для USDC
    },
    'USDT': {
        'abi': USDT_ABI,
        'address': 0x068f5c6a61780768455de69077e07e89787839bf8166decfbf92b645209c0fb8,
        'decimals': 6,
        'approve_address': 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
        'pool_id': 4  # pool_id для USDC
    },
    'DAI': {
        'abi': DAI_ABI,
        'address': 0x00da114221cb83fa859dbdb4c44beeaa0bb37c7537ad5ae66fe5e0efd20e6eb3,
        'decimals': 18,
        'approve_address': 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28,
        'pool_id': 2  # pool_id для USDC
    },
    'ETH': {
        'abi': ABI_ETH,
        'address': 0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7,
        'decimals': 18,
        'approve_address': 0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28
    }
}