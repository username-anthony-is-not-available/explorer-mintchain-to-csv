from typing import Union
from models import RawTokenTransfer, RawTransaction

# A sample list of DeFi router addresses, organized by chain
DEFI_ROUTERS = {
    "etherscan": {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router 2
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8660fc45",  # Uniswap V3 Router 2
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
    },
    "basescan": {
        "0x2626664c2603336e57b271c5c0b26d2464912bb4",  # Uniswap V3 Router (Base)
        "0xbe2133400b95767b347b4d3cca1b576871de388b",  # BaseSwap Router
    },
    "arbiscan": {
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap (Arbitrum)
    },
    "mintchain": {
        # Add MintChain DeFi routers here if applicable
    }
}

AnyRawTransaction = Union[RawTransaction, RawTokenTransfer]

def categorize_transaction(transaction: AnyRawTransaction, chain: str) -> str:
    """
    Categorizes a transaction based on its type and attributes.
    Returns a Koinly-compatible label.
    """
    to_address = ""
    if hasattr(transaction, 'to_address') and hasattr(transaction.to_address, 'hash'):
        to_address = transaction.to_address.hash.lower()

    # Get the set of DeFi routers for the specified chain
    chain_routers = DEFI_ROUTERS.get(chain, set())

    if to_address in chain_routers:
        return "swap"

    if isinstance(transaction, RawTokenTransfer):
        # ERC-721 NFTs typically have 0 decimals.
        if hasattr(transaction, 'tokenDecimal') and transaction.tokenDecimal == '0':
            return "nft_transfer"
        return "token_transfer"

    if isinstance(transaction, RawTransaction):
        return "transfer"

    return "" # Default for simple transfers, deposits, withdrawals.
