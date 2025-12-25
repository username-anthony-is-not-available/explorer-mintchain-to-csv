from typing import Union
from models import RawTokenTransfer, RawTransaction

# A sample list of DeFi router addresses (Uniswap on Ethereum)
# This should be expanded based on the chains and DEXs supported.
DEFI_ROUTERS = {
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router 2
    "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
    "0x68b3465833fb72a70ecdf485e0e4c7bd8660fc45",  # Uniswap V3 Router 2
}

AnyRawTransaction = Union[RawTransaction, RawTokenTransfer]

def categorize_transaction(transaction: AnyRawTransaction) -> str:
    """
    Categorizes a transaction based on its type and attributes.
    Returns a Koinly-compatible label.
    """
    to_address = ""
    if isinstance(transaction, RawTransaction):
        to_address = transaction.to_address.hash
    elif isinstance(transaction, RawTokenTransfer):
        to_address = transaction.to_address.hash

    if to_address.lower() in DEFI_ROUTERS:
        return "swap"

    if isinstance(transaction, RawTokenTransfer):
        # ERC-721 NFTs typically have 0 decimals.
        if hasattr(transaction, 'tokenDecimal') and transaction.tokenDecimal == '0':
            # Koinly doesn't have a specific NFT label. Users often handle them manually.
            # We can leave the label empty or use a generic one.
            # Let's return a specific label for now, can be adjusted.
            return "nft_transfer"

    return "" # Default for simple transfers, deposits, withdrawals.
