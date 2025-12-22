from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException
import pytest

from fetch_blockchain_data import fetch_data
from models import RawTransaction

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
