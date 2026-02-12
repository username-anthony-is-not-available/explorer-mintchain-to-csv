from models import RawTokenTransfer, RawTransaction
from extract_transaction_data import extract_transaction_data

# Mock data for testing
WALLET_ADDRESS = "test_wallet"

MOCK_TRANSACTION = RawTransaction.model_validate({
    "timeStamp": "1673784000",
    "value": "1000000000000000000",
    "gasUsed": "21000",
    "gasPrice": "1000000000",
    "hash": "0x123",
    "from": {"hash": WALLET_ADDRESS},
    "to": {"hash": "recipient"},
})

MOCK_TOKEN_TRANSFER = RawTokenTransfer.model_validate({
    "timeStamp": "1676894400",
    "total": {"value": "10000000000000000000"},
    "token": {"symbol": "TOK"},
    "hash": "0x456",
    "from": {"hash": "sender"},
    "to": {"hash": WALLET_ADDRESS},
    "tokenDecimal": "18",
})

def test_extract_transaction_data_sent():
    """Tests that sent transactions are correctly processed."""
    data = extract_transaction_data([MOCK_TRANSACTION], "transaction", WALLET_ADDRESS, "mintchain")
    assert len(data) == 1
    trx = data[0]
    assert trx.sent_amount == "1"
    assert trx.sent_currency == "ETH"
    assert trx.received_amount is None
    assert trx.fee_amount == "0.000021"

def test_extract_token_transfer_received():
    """Tests that received token transfers are correctly processed."""
    data = extract_transaction_data([MOCK_TOKEN_TRANSFER], "token_transfers", WALLET_ADDRESS, "mintchain")
    assert len(data) == 1
    trx = data[0]
    assert trx.received_amount == "10"
    assert trx.received_currency == "TOK"
    assert trx.sent_amount is None
    assert trx.fee_amount is None
