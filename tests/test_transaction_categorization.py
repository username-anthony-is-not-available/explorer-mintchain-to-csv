import pytest
from models import RawTokenTransfer, RawTransaction, Address, Token, Total
from transaction_categorization import categorize_transaction, DEFI_ROUTERS

@pytest.fixture
def swap_transaction() -> RawTransaction:
    """Fixture for a swap transaction to a known DeFi router."""
    return RawTransaction.model_validate({
        "hash": "0xswaphash",
        "timeStamp": "1672531200",
        "from": {"hash": "0xfrom"},
        "to": {"hash": list(DEFI_ROUTERS)[0]},
        "value": "1000000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

@pytest.fixture
def nft_transfer() -> RawTokenTransfer:
    """Fixture for a typical NFT transfer."""
    return RawTokenTransfer.model_validate({
        "hash": "0xnfthash",
        "timeStamp": "1672531201",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xto"},
        "total": {"value": "1"},
        "token": {"symbol": "NFT"},
        "tokenDecimal": "0",
    })

@pytest.fixture
def simple_transfer() -> RawTransaction:
    """Fixture for a simple transfer not involving any special addresses."""
    return RawTransaction.model_validate({
        "hash": "0xsimplehash",
        "timeStamp": "1672531202",
        "from": {"hash": "0xfrom"},
        "to": {"hash": "0xanotheraddress"},
        "value": "500000000000000000",
        "gasUsed": "21000",
        "gasPrice": "50000000000",
    })

def test_categorize_swap_transaction(swap_transaction: RawTransaction) -> None:
    """Test that a transaction to a DeFi router is labeled as a 'swap'."""
    label = categorize_transaction(swap_transaction)
    assert label == "swap"

def test_categorize_nft_transfer(nft_transfer: RawTokenTransfer) -> None:
    """Test that a token transfer with 0 decimals is labeled as 'nft_transfer'."""
    label = categorize_transaction(nft_transfer)
    assert label == "nft_transfer"

def test_categorize_simple_transfer(simple_transfer: RawTransaction) -> None:
    """Test that a standard transaction has no label."""
    label = categorize_transaction(simple_transfer)
    assert label == ""
