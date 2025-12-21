import pytest
import requests
from unittest.mock import patch, MagicMock
from extract_transaction_data import extract_transaction_data
from fetch_blockchain_data import fetch_data

# Mock data for testing
WALLET_ADDRESS = "test_wallet"

MOCK_TRANSACTION = {
    "timeStamp": "2023-01-15T12:00:00.000Z",
    "value": "1",
    "gasUsed": "21000",
    "gasPrice": "1000000000",
    "hash": "0x123",
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
    assert trx["Fee Amount"] == "0.000021"

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
def test_fetch_data_success(mock_get):
    """Tests fetch_data with a successful API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": [{"id": 1}, {"id": 2}]}
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api")
    assert result == [{"id": 1}, {"id": 2}]
    mock_get.assert_called_once_with("http://test.com/api", timeout=10)


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_api_error(mock_get):
    """Tests fetch_data with an API error response."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api")
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_request_exception(mock_get):
    """Tests fetch_data with a request exception."""
    mock_get.side_effect = requests.exceptions.RequestException("Test error")

    result = fetch_data("http://test.com/api")
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_no_result_list(mock_get):
    """Tests fetch_data with a response that does not contain a list in 'result'."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "not a list"}
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api")
    assert result == []
