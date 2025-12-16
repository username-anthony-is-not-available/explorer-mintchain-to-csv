import pytest
from unittest.mock import patch, MagicMock
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import fetch_data

# Mock data for testing
WALLET_ADDRESS = "test_wallet"

MOCK_TRANSACTION = {
    "timestamp": "2023-01-15T12:00:00.000Z",
    "value": "1",
    "fee": "0.01",
    "tx_hash": "0x123",
    "from": {"hash": WALLET_ADDRESS},
    "to": {"hash": "recipient"},
    "type": "transaction"
}

MOCK_TOKEN_TRANSFER = {
    "timestamp": "2023-02-20T12:00:00.000Z",
    "total": {"value": "10"},
    "token": {"symbol": "TOK"},
    "tx_hash": "0x456",
    "from": {"hash": "sender"},
    "to": {"hash": WALLET_ADDRESS},
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
    assert trx["Fee Amount"] == "0.01"

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
            "items": [{"id": 1}],
            "next_page_params": {"page": 2}
        }),
        MagicMock(status_code=200, json=lambda: {
            "items": [{"id": 2}],
            "next_page_params": None
        })
    ]

    items = fetch_data("http://test.com/api?page=1")
    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[1]["id"] == 2
