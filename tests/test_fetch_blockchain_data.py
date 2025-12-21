from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException

from fetch_blockchain_data import fetch_data, fetch_transactions, fetch_token_transfers, fetch_internal_transactions


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'result': [{'tx': '1'}]}
    mock_get.return_value = mock_response

    result = fetch_data('http://test.com')
    assert result == [{'tx': '1'}]


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_non_200_status(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = fetch_data('http://test.com')
    assert result == []


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_invalid_json(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'no result key'}
    mock_get.return_value = mock_response

    result = fetch_data('http://test.com')
    assert result == []


@patch('fetch_blockchain_data.requests.get', side_effect=RequestException('Request failed'))
def test_fetch_data_request_exception(mock_get):
    result = fetch_data('http://test.com')
    assert result == []


@patch('fetch_blockchain_data.fetch_data')
def test_fetch_transactions(mock_fetch_data):
    mock_fetch_data.return_value = [{'tx': '1'}]
    result = fetch_transactions('0x123')
    assert result == [{'tx': '1'}]
    mock_fetch_data.assert_called_once()


@patch('fetch_blockchain_data.fetch_data')
def test_fetch_token_transfers(mock_fetch_data):
    mock_fetch_data.return_value = [{'tx': '2'}]
    result = fetch_token_transfers('0x123')
    assert result == [{'tx': '2'}]
    mock_fetch_data.assert_called_once()


@patch('fetch_blockchain_data.fetch_data')
def test_fetch_internal_transactions(mock_fetch_data):
    mock_fetch_data.return_value = [{'tx': '3'}]
    result = fetch_internal_transactions('0x123')
    assert result == [{'tx': '3'}]
    mock_fetch_data.assert_called_once()
