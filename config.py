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

# Timeout value (in seconds)
TIMEOUT: int = 10
