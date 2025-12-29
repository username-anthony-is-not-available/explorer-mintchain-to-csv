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
