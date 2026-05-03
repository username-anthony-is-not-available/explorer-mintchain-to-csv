# Explorer base URLs
EXPLORER_URLS = {
    'mintchain': 'https://api.routescan.io/v2/network/mainnet/evm/185/etherscan',
    'etherscan': 'https://api.etherscan.io/api',
    'basescan': 'https://api.basescan.org/api',
    'arbiscan': 'https://api.arbiscan.io/api',
    'optimism': 'https://api-optimistic.etherscan.io/api',
    'polygon': 'https://api.polygonscan.com/api',
}

# Explorer API keys
EXPLORER_API_KEYS = {
    'etherscan': 'ETHERSCAN_API_KEY',
    'basescan': 'BASESCAN_API_KEY',
    'arbiscan': 'ARBISCAN_API_KEY',
    'optimism': 'OPTIMISM_API_KEY',
    'polygon': 'POLYGON_API_KEY',
}

# Native currencies by chain
NATIVE_CURRENCIES = {
    'mintchain': 'ETH',
    'etherscan': 'ETH',
    'basescan': 'ETH',
    'arbiscan': 'ETH',
    'optimism': 'ETH',
    'polygon': 'MATIC',
}

# Coingecko configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_PLATFORM_MAP = {
    'ethereum': 'ethereum',
    'etherscan': 'ethereum',
    'polygon': 'polygon-pos',
    'basescan': 'base',
    'arbiscan': 'arbitrum-one',
    'optimism': 'optimistic-ethereum',
    'mintchain': 'mint-blockchain',  # Placeholder if not officially supported yet
}

# DefiLlama configuration
DEFILLAMA_BASE_URL = "https://coins.llama.fi"
DEFILLAMA_COIN_MAP = {
    "ETH": "ethereum",
    "MATIC": "polygon",
    "BNB": "binancecoin",
    "ARB": "arbitrum",
    "OP": "optimism",
}
DEFILLAMA_PLATFORM_MAP = {
    "ethereum": "ethereum",
    "etherscan": "ethereum",
    "polygon": "polygon-pos",
    "basescan": "base",
    "arbiscan": "arbitrum-one",
    "optimism": "optimistic-ethereum",
    "mintchain": "mint-blockchain",
}

# Timeout value (in seconds)
TIMEOUT: int = 10
