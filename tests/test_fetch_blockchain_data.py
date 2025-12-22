from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
import pytest

from fetch_blockchain_data import fetch_data, fetch_internal_transactions, fetch_token_transfers
from models import RawTokenTransfer, RawTransaction

@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_success(mock_get):
    """Tests fetch_data with a successful API response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": [
            {
                "hash": "0xabc",
                "timeStamp": "1234567890",
                "from": {"hash": "0xfrom"},
                "to": {"hash": "0xto"},
                "value": "1000",
                "gasUsed": "21000",
                "gasPrice": "50"
            }
        ]
    }
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api", RawTransaction)
    assert len(result) == 1
    assert isinstance(result[0], RawTransaction)
    assert result[0].hash == "0xabc"


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_api_error(mock_get):
    """Tests fetch_data with an API error response."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = RequestException
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api", RawTransaction)
    assert result == []


@patch('fetch_blockchain_data.fetch_data')
def test_fetch_token_transfers_success(mock_fetch_data):
    """Tests fetch_token_transfers with a successful API response."""
    mock_fetch_data.return_value = [
        RawTokenTransfer.model_validate({
            "hash": "0xdef",
            "timeStamp": "1234567891",
            "from": {"hash": "0xfrom"},
            "to": {"hash": "0xto"},
            "total": {"value": "2000"},
            "token": {"symbol": "TKN"}
        })
    ]

    result = fetch_token_transfers("0x123")
    assert len(result) == 1
    assert isinstance(result[0], RawTokenTransfer)
    assert result[0].hash == "0xdef"
    mock_fetch_data.assert_called_once()


@patch('fetch_blockchain_data.fetch_data')
def test_fetch_internal_transactions_success(mock_fetch_data):
    """Tests fetch_internal_transactions with a successful API response."""
    mock_fetch_data.return_value = [
        RawTransaction.model_validate({
            "hash": "0xghi",
            "timeStamp": "1234567892",
            "from": {"hash": "0xfrom"},
            "to": {"hash": "0xto"},
            "value": "3000",
            "gasUsed": "23000",
            "gasPrice": "70"
        })
    ]

    result = fetch_internal_transactions("0x123")
    assert len(result) == 1
    assert isinstance(result[0], RawTransaction)
    assert result[0].hash == "0xghi"
    mock_fetch_data.assert_called_once()


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_validation_error(mock_get):
    """Tests fetch_data with a validation error for an item."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": [
            {
                "hash": "0xabc",
                # "timeStamp" is missing to cause a validation error
                "from": {"hash": "0xfrom"},
                "to": {"hash": "0xto"},
                "value": "1000",
                "gasUsed": "21000",
                "gasPrice": "50"
            }
        ]
    }
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api", RawTransaction)
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_unexpected_exception(mock_get):
    """Tests fetch_data with an unexpected exception."""
    mock_get.side_effect = Exception("Unexpected error")

    result = fetch_data("http://test.com/api", RawTransaction)
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_request_exception(mock_get):
    """Tests fetch_data with a request exception."""
    mock_get.side_effect = RequestException("Test error")

    result = fetch_data("http://test.com/api", RawTransaction)
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_no_result_list(mock_get):
    """Tests fetch_data with a response that does not contain a list in 'result'."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "not a list"}
    mock_get.return_value = mock_response

    result = fetch_data("http://test.com/api", RawTransaction)
    assert result == []
