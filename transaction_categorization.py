from decimal import Decimal
from typing import List, Union
from models import Raw1155Transfer, RawNFTTransfer, RawTokenTransfer, RawTransaction, TransactionType

# A sample list of DeFi router addresses, organized by chain
DEFI_ROUTERS = {
    "etherscan": {
        "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",  # Uniswap V2 Router 2
        "0xe592427a0aece92de3edee1f18e0157c05861564",  # Uniswap V3 Router
        "0x68b3465833fb72a70ecdf485e0e4c7bd8660fc45",  # Uniswap V3 Router 2
        "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f",  # SushiSwap Router
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router
        "0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b",  # Uniswap Universal Router V1
        "0x66a9893cc07d91d95644aedd05d03f95e1dba8af",  # Uniswap Universal Router V2
    },
    "basescan": {
        "0x2626664c2603336e57b271c5c0b26d2464912bb4",  # Uniswap V3 Router (Base)
        "0xbe2133400b95767b347b4d3cca1b576871de388b",  # BaseSwap Router
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad",  # Uniswap Universal Router
        "0x6ff5693b99212da76ad316178a184ab56d299b43",  # Uniswap Universal Router V2
    },
    "arbiscan": {
        "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506",  # SushiSwap (Arbitrum)
        "0x5e325eda8064b456f4781070c0738d849c824258",  # Uniswap Universal Router
        "0xa51afafe0263b40edaef0df8781ea9aa03e381a3",  # Uniswap Universal Router V2
    },
    "optimism": {
        "0xcb1355ff08ab38bbce60111f1bb2b784be25d7e8",  # Uniswap Universal Router
        "0x851116d9223fabed8e56c0e6b8ad0c31d98b3507",  # Uniswap Universal Router V2
    },
    "polygon": {
        "0xec7be89e9d109e7e3fec59c222cf297125fefda2",  # Uniswap Universal Router
        "0x1095692a6237d83c6a72f3f5efedb9a670c49223",  # Uniswap Universal Router V2
    },
    "mintchain": {
        "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a",  # Mintchain SwapRouter
        "0x13f4395944a2353e81e2975988e65a20da192bc7",  # PancakeSwap V3 Router
        "0x1b81d7788448729965a3bc5573479e00a9075306",  # MintChain DEX Router
    }
}

LENDING_PROTOCOLS = {
    "etherscan": {
        "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",  # Aave V3 Pool
    },
    "basescan": {
        "0xa238dd80c259a72e81d7e4664a9801593f98d1c5",  # Aave V3 Pool
    },
    "arbiscan": {
        "0x794a61358d6845594f94dc1db02a252b5b4814ad",  # Aave V3 Pool
    },
    "optimism": {
        "0x794a61358d6845594f94dc1db02a252b5b4814ad",  # Aave V3 Pool
    },
    "polygon": {
        "0x794a61358d6845594f94dc1db02a252b5b4814ad",  # Aave V3 Pool
    }
}

BRIDGE_CONTRACTS = {
    "etherscan": {
        "0x2b3f201543adf73160ba42e1a5b7750024f30420",  # MintChain L1StandardBridge
        "0xc2c908f3226d9082130d8e48378cd2efb08b521d",  # MintChain L1ERC721Bridge
        "0x8922883499e90956e3d237194d7423d9e0b08006",  # OptimismPortal
        "0x194589998064f25ff15a3677a003d14f67a3ae8b",  # L1CrossDomainMessenger
    },
    "mintchain": {
        "0x4200000000000000000000000000000000000010",  # L2StandardBridge
        "0x4200000000000000000000000000000000000014",  # L2ERC721Bridge
        "0x4200000000000000000000000000000000000007",  # L2CrossDomainMessenger
        "0x4200000000000000000000000000000000000016",  # L2ToL1MessagePasser
    }
}

STAKING_CONTRACTS = {
    "mintchain": {
        "0x2e8697157321681285227092892994469e38f921",  # MintPool sMINT (placeholder example)
    }
}

AnyRawTransaction = Union[RawTransaction, RawTokenTransfer, RawNFTTransfer, Raw1155Transfer]

def categorize_transaction(transaction: AnyRawTransaction, chain: str = 'mintchain') -> str:
    """
    Categorizes a transaction based on its type and attributes.
    Returns a Koinly-compatible label.
    """
    to_address = ""
    from_address = ""
    
    if hasattr(transaction, 'to_address') and hasattr(transaction.to_address, 'hash'):
        to_address = transaction.to_address.hash.lower()
    
    if hasattr(transaction, 'from_address') and hasattr(transaction.from_address, 'hash'):
        from_address = transaction.from_address.hash.lower()

    # Get the set of DeFi routers for the specified chain
    chain_routers = DEFI_ROUTERS.get(chain, set())
    chain_bridge_contracts = BRIDGE_CONTRACTS.get(chain, set())
    chain_staking_contracts = STAKING_CONTRACTS.get(chain, set())
    chain_lending_protocols = LENDING_PROTOCOLS.get(chain, set())

    if to_address in chain_routers:
        return TransactionType.SWAP.value
    if to_address in chain_bridge_contracts or from_address in chain_bridge_contracts:
        return TransactionType.BRIDGE.value
    if to_address in chain_staking_contracts or from_address in chain_staking_contracts:
        return TransactionType.STAKING.value
    if to_address in chain_lending_protocols:
        return TransactionType.LEND.value

    # Detect Minting (from 0x00...00)
    if from_address == "0x0000000000000000000000000000000000000000":
        return TransactionType.MINT.value

    # Detect Burning (to 0x00...00 or dead address)
    if to_address == "0x0000000000000000000000000000000000000000" or \
       to_address == "0x000000000000000000000000000000000000dead":
        return TransactionType.BURN.value

    if isinstance(transaction, (RawTokenTransfer, RawNFTTransfer, Raw1155Transfer)):
        if isinstance(transaction, RawNFTTransfer) or \
           (isinstance(transaction, RawTokenTransfer) and getattr(transaction, 'tokenDecimal', None) == '0'):
            return TransactionType.NFT_TRANSFER.value
        return TransactionType.TOKEN_TRANSFER.value

    if isinstance(transaction, RawTransaction):
        # Detect Cost (value 0, but gas was paid)
        if getattr(transaction, 'value', '0') == '0' and \
           getattr(transaction, 'gasPrice', None) and \
           getattr(transaction, 'gasUsed', None):
            return TransactionType.COST.value
        return TransactionType.TRANSFER.value

    return "" # Default for simple transfers, deposits, withdrawals.


def detect_swap_from_transfers(transactions: List) -> str:
    """
    Heuristic to detect a swap or liquidity event based on the presence of
    sent and received assets within a single transaction hash.
    """
    sent_currencies = set()
    received_currencies = set()

    for tx in transactions:
        # Check if it has a sent amount
        sent_amount = getattr(tx, 'sent_amount', None)
        sent_currency = getattr(tx, 'sent_currency', None)
        if sent_amount and Decimal(str(sent_amount)) > 0 and sent_currency:
            sent_currencies.add(sent_currency)

        # Check if it has a received amount
        received_amount = getattr(tx, 'received_amount', None)
        received_currency = getattr(tx, 'received_currency', None)
        if received_amount and Decimal(str(received_amount)) > 0 and received_currency:
            received_currencies.add(received_currency)

    # Liquidity Addition: 2+ tokens sent, 1 received (the LP token)
    if len(sent_currencies) >= 2 and len(received_currencies) == 1:
        return TransactionType.LIQUIDITY_ADD.value

    # Liquidity Removal: 1 token sent (the LP token), 2+ received
    if len(sent_currencies) == 1 and len(received_currencies) >= 2:
        return TransactionType.LIQUIDITY_REMOVE.value

    # Swap: 1 sent, 1 received (or multi-hop but still essentially a swap)
    if sent_currencies and received_currencies:
        return TransactionType.SWAP.value

    return ""
