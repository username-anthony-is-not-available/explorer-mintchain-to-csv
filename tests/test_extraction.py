import pytest
from unittest.mock import patch, MagicMock
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import fetch_data

# Mock data for testing
WALLET_ADDRESS = "test_wallet"

MOCK_TRANSACTION = {
    "timeStamp": "1673784000",
    "value": "1",
    "gasUsed": "21000",
    "gasPrice": "1000000000",
    "hash": "0x123",
    "from": WALLET_ADDRESS,
    "to": "recipient",
    "type": "transaction"
}

MOCK_TOKEN_TRANSFER = {
    "timeStamp": "1676894400",
    "value": "10",
    "tokenSymbol": "TOK",
    "hash": "0x456",
    "from": "sender",
    "to": WALLET_ADDRESS,
    "type": "token_transfer"
}

def test_extract_transaction_data_sent():
    """Tests that sent transactions are correctly processed."""
    data = extract_transaction_data([MOCK_TRANSACTION], "transaction", WALLET_ADDRESS)
    assert len(data) == 1
    trx = data[0]
    assert trx["Sent Amount"] == "1"
    assert trx["Sent Currency"] == "ETH"
    assert trx["Received Amount"] == ""
    assert trx["Fee Amount"] == "21000000000000"

def test_extract_token_transfer_received():
    """Tests that received token transfers are correctly processed."""
    data = extract_transaction_data([MOCK_TOKEN_TRANSFER], "token_transfers", WALLET_ADDRESS)
    assert len(data) == 1
    trx = data[0]
    assert trx["Received Amount"] == "10"
    assert trx["Received Currency"] == "TOK"
    assert trx["Sent Amount"] == ""
    assert trx["Fee Amount"] == ""

@patch('fetch_blockchain_data.requests.get')
def test_pagination_logic(mock_get):
    """Tests that pagination is handled correctly."""
    # Mock the first page of the API response
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda: {
            "result": [{"id": 1}],
            "next_page_params": {"page": 2}
        }),
        MagicMock(status_code=200, json=lambda: {
            "result": [{"id": 2}],
            "next_page_params": None
        })
    ]

    items = fetch_data("http://test.com/api?page=1")
    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[1]["id"] == 2
