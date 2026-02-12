import pytest
from models import Address, RawTokenTransfer, RawTransaction, Token, Total
from transaction_categorization import categorize_transaction

# Mock data for testing
def create_mock_raw_transaction(to_address: str) -> RawTransaction:
    """Factory function to create a mock RawTransaction."""
    return RawTransaction.model_validate({
        "hash": "0x123",
        "timeStamp": "1672531200",
        "from": {"hash": "0xfrom"},
        "to": {"hash": to_address},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

def create_mock_raw_token_transfer(to_address: str, token_decimal: str) -> RawTokenTransfer:
    """Factory function to create a mock RawTokenTransfer."""
    return RawTokenTransfer.model_validate({
        "hash": "0x456",
        "timeStamp": "1672531201",
        "from": {"hash": "0xfrom"},
        "to": {"hash": to_address},
        "total": {"value": "100"},
        "token": {"symbol": "TKN"},
        "tokenDecimal": token_decimal,
    })

# Test cases
def test_categorize_as_swap():
    """Test that a transaction to a DeFi router is categorized as a swap."""
    # Using a known Uniswap V2 router address
    uniswap_router = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
    transaction = create_mock_raw_transaction(uniswap_router)
    assert categorize_transaction(transaction, "etherscan") == "swap"

@pytest.fixture
def swap_transaction() -> RawTransaction:
    """Fixture for a swap transaction to a known DeFi router."""
    # Use a router from the 'etherscan' list for this generic test
    # Assuming DEFI_ROUTERS is imported or defined elsewhere for this fixture to work
    # For the purpose of this edit, we'll use a placeholder if DEFI_ROUTERS is not in the provided context.
    # If DEFI_ROUTERS is not defined, this fixture will cause an error.
    # To make it syntactically correct without DEFI_ROUTERS, we'll use a hardcoded address.
    # If DEFI_ROUTERS is expected to be imported, please ensure it is.
    router_address = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d" # Placeholder for list(DEFI_ROUTERS["etherscan"])[0]
    return RawTransaction.model_validate({
        "hash": "0xswaphash",
        "timeStamp": "1672531200",
        "from": {"hash": "0xfrom"},
        "to": {"hash": router_address},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

@pytest.fixture
def mintchain_swap_transaction() -> RawTransaction:
    """Fixture for a swap transaction on Mintchain."""
    return RawTransaction.model_validate({
        "hash": "0xmintchainswaphash",
        "timeStamp": "1672531200",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a"},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

@pytest.fixture
def mint_transaction() -> RawTransaction:
    """Fixture for a mint transaction."""
    return RawTransaction.model_validate({
        "hash": "0xminthash",
        "timeStamp": "1672531200",
        "from": {"hash": "0x0000000000000000000000000000000000000000"},
        "to": {"hash": "0xreceiver"},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

@pytest.fixture
def burn_transaction() -> RawTransaction:
    """Fixture for a burn transaction."""
    return RawTransaction.model_validate({
        "hash": "0xburnhash",
        "timeStamp": "1672531200",
        "from": {"hash": "0xsender"},
        "to": {"hash": "0x000000000000000000000000000000000000dEaD"},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

def test_categorize_swap_transaction(swap_transaction: RawTransaction) -> None:
    """Test that a transaction to a DeFi router is labeled as a 'swap'."""
    # We used an etherscan router in the fixture, so we must pass 'etherscan' as the chain
    label = categorize_transaction(swap_transaction, chain='etherscan')
    assert label == "swap"

def test_categorize_mintchain_swap_transaction(mintchain_swap_transaction: RawTransaction) -> None:
    """Test that a Mintchain swap transaction is labeled as a 'swap'."""
    label = categorize_transaction(mintchain_swap_transaction)
    assert label == "swap"

def test_categorize_mint_transaction(mint_transaction: RawTransaction) -> None:
    """Test that a mint transaction is labeled as 'mint'."""
    label = categorize_transaction(mint_transaction)
    assert label == "mint"

def test_categorize_burn_transaction(burn_transaction: RawTransaction) -> None:
    """Test that a burn transaction is labeled as 'burn'."""
    label = categorize_transaction(burn_transaction)
    assert label == "burn"

def test_categorize_as_nft_transfer():
    """Test that a token transfer with 0 decimals is categorized as an NFT transfer."""
    transaction = create_mock_raw_token_transfer("0xrecipient", "0")
    assert categorize_transaction(transaction, "mintchain") == "nft_transfer"

def test_categorize_as_token_transfer():
    """Test that a regular token transfer is categorized as a token transfer."""
    transaction = create_mock_raw_token_transfer("0xrecipient", "18")
    assert categorize_transaction(transaction, "mintchain") == "token_transfer"

def test_categorize_as_simple_transfer():
    """Test that a standard ETH transfer is categorized as a transfer."""
    transaction = create_mock_raw_transaction("0xrecipient")
    assert categorize_transaction(transaction, "mintchain") == "transfer"

def test_categorize_with_unknown_address():
    """Test that a transaction to an unknown address is categorized as a transfer."""
    transaction = create_mock_raw_transaction("0xunknown")
    assert categorize_transaction(transaction, "mintchain") == "transfer"

def test_categorize_as_bridge_l1():
    """Test that a transaction to an L1 bridge contract is categorized as a bridge on etherscan."""
    bridge_address = "0x2b3f201543adf73160ba42e1a5b7750024f30420"
    transaction = create_mock_raw_transaction(bridge_address)
    assert categorize_transaction(transaction, "etherscan") == "bridge"

def test_categorize_as_bridge_l2():
    """Test that a transaction to an L2 bridge contract is categorized as a bridge on mintchain."""
    bridge_address = "0x4200000000000000000000000000000000000010"
    transaction = create_mock_raw_transaction(bridge_address)
    assert categorize_transaction(transaction, "mintchain") == "bridge"

def test_categorize_as_bridge_incoming():
    """Test that a transaction from a bridge contract is categorized as a bridge."""
    bridge_address = "0x4200000000000000000000000000000000000010"
    raw_trx_data = {
        "hash": "0xbridge_incoming",
        "timeStamp": "1672531200",
        "from": {"hash": bridge_address},
        "to": {"hash": "0xuser"},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    }
    transaction = RawTransaction.model_validate(raw_trx_data)
    assert categorize_transaction(transaction, "mintchain") == "bridge"
