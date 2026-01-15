import logging
from unittest.mock import MagicMock, Mock, call, patch

import pytest
import responses
import requests
from requests.exceptions import HTTPError, RequestException

from config import EXPLORER_URLS
from explorer_adapters import (
    ArbiscanAdapter,
    BasescanAdapter,
    EtherscanAdapter,
    MintchainAdapter,
)
from fetch_blockchain_data import fetch_data
from models import RawTokenTransfer, RawTransaction

WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"
CHAIN = "mintchain"
ADAPTERS = {
    "mintchain": MintchainAdapter,
    "etherscan": EtherscanAdapter,
    "basescan": BasescanAdapter,
    "arbiscan": ArbiscanAdapter,
}


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_adapter_get_transactions_success(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={
            "result": [
                {
                    "hash": "0xabc",
                    "from": {"hash": "0x123"},
                    "to": {"hash": "0x456"},
                    "value": "100",
                    "timeStamp": "1672531200",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                }
            ]
        },
        status=200,
    )
    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert transactions[0].hash == "0xabc"


def test_adapter_get_transactions_failure(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(responses.GET, mock_url, status=500)
    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0


def test_adapter_get_transactions_validation_error(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"result": [{"hash": "0xabc"}]},  # Missing required fields
        status=200,
    )
    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0


def test_adapter_get_transactions_malformed_response(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"data": "not a result list"},  # Malformed response
        status=200,
    )
    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0


def test_adapter_get_token_transfers_success(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=tokentx&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={
            "result": [
                {
                    "hash": "0xdef",
                    "from": {"hash": "0x123"},
                    "to": {"hash": "0x456"},
                    "timeStamp": "1672531201",
                    "total": {"value": "200"},
                    "token": {"symbol": "TKN"},
                    "tokenDecimal": "18",
                }
            ]
        },
        status=200,
    )
    transfers = adapter.get_token_transfers(WALLET_ADDRESS)
    assert len(transfers) == 1
    assert transfers[0].hash == "0xdef"


def test_adapter_get_internal_transactions_success(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlistinternal&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={
            "result": [
                {
                    "hash": "0xghi",
                    "from": {"hash": "0x123"},
                    "to": {"hash": "0x456"},
                    "value": "300",
                    "timeStamp": "1672531202",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                }
            ]
        },
        status=200,
    )
    transactions = adapter.get_internal_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert transactions[0].hash == "0xghi"


@patch("requests.get")
def test_fetch_data_retry_logic(mock_get, caplog):
    # Configure the mock to raise a RequestException 5 times
    mock_get.side_effect = RequestException("Test Exception")
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    with caplog.at_level(logging.ERROR):
        result = fetch_data(mock_url, RawTransaction)

    # Check that the function was called 5 times
    assert mock_get.call_count == 5

    # Check that the result is an empty list
    assert result == []

    # Check that the error was logged
    assert "An error occurred while fetching data after multiple retries" in caplog.text


@patch("time.sleep", return_value=None)
@responses.activate
def test_fetch_data_rate_limiting_logic(mock_sleep, caplog):
    # Configure the mock to return a 429 error with a Retry-After header
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    # Mock the first 4 calls to fail with a 429, and the 5th to also fail
    for _ in range(5):
        responses.add(
            responses.GET,
            mock_url,
            status=429,
            headers={"Retry-After": "10"},
        )

    with caplog.at_level(logging.WARNING):
        result = fetch_data(mock_url, RawTransaction)

    # Check that the function was called 5 times
    assert len(responses.calls) == 5

    # Check that sleep was called with the correct delay 4 times
    assert mock_sleep.call_count == 4
    mock_sleep.assert_has_calls([call(10)] * 4)

    # Check that the warning was logged
    assert "Rate limit exceeded. Retrying after 10 seconds." in caplog.text

    # Check that the result is an empty list
    assert result == []


@patch("requests.get")
def test_fetch_data_retry_on_server_error(mock_get, caplog):
    # Configure the mock to raise an HTTPError for a server-side error (e.g., 500)
    mock_response = Mock()
    mock_response.status_code = 500
    mock_http_error = HTTPError("Server Error")
    mock_http_error.response = mock_response
    mock_response.raise_for_status.side_effect = mock_http_error
    mock_get.return_value = mock_response

    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    with caplog.at_level(logging.ERROR):
        result = fetch_data(mock_url, RawTransaction)

    # Check that the function was retried
    assert mock_get.call_count == 5

    # Check that the result is an empty list
    assert result == []

    # Check that the final error was logged after all retries
    assert "An error occurred while fetching data after multiple retries" in caplog.text


@patch("requests.get")
def test_fetch_data_retry_on_request_exception(mock_get):
    # Configure the mock to raise a RequestException 3 times, then succeed
    mock_get.side_effect = [
        RequestException("Attempt 1"),
        RequestException("Attempt 2"),
        RequestException("Attempt 3"),
        # Mock a successful response
        Mock(
            status_code=200,
            json=lambda: {
                "result": [
                    {
                        "hash": "0xabc",
                        "from": {"hash": "0x123"},
                        "to": {"hash": "0x456"},
                        "value": "100",
                        "timeStamp": "1672531200",
                        "gasUsed": "21000",
                        "gasPrice": "1000000000",
                    }
                ]
            },
        ),
    ]
    base_url = EXPLORER_URLS[CHAIN]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    # Call the function
    result = fetch_data(mock_url, RawTransaction)

    # Check that requests.get was called 4 times
    assert mock_get.call_count == 4


def test_adapter_unsupported_chain():
    adapter = MintchainAdapter("invalidchain")
    with pytest.raises(ValueError, match="Unsupported chain: invalidchain"):
        adapter.get_transactions(WALLET_ADDRESS)


@pytest.mark.parametrize("chain", ["etherscan", "basescan", "arbiscan"])
def test_adapter_with_api_key(mocked_responses, monkeypatch, chain):
    adapter_class = ADAPTERS[chain]
    adapter = adapter_class(chain)
    api_key_env_var = {
        "etherscan": "ETHERSCAN_API_KEY",
        "basescan": "BASESCAN_API_KEY",
        "arbiscan": "ARBISCAN_API_KEY",
    }[chain]
    test_api_key = "TEST_API_KEY"
    monkeypatch.setenv(api_key_env_var, test_api_key)

    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&apikey={test_api_key}"

    mocked_responses.add(
        responses.GET,
        mock_url,
        json={
            "result": [
                {
                    "hash": "0xabc",
                    "from": {"hash": "0x123"},
                    "to": {"hash": "0x456"},
                    "value": "100",
                    "timeStamp": "1672531200",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                }
            ]
        },
        status=200,
    )

    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert transactions[0].hash == "0xabc"
    assert len(mocked_responses.calls) == 1
    assert mocked_responses.calls[0].request.url == mock_url


@pytest.mark.parametrize("chain", ["etherscan", "basescan", "arbiscan"])
def test_adapter_without_api_key(mocked_responses, monkeypatch, chain):
    adapter_class = ADAPTERS[chain]
    adapter = adapter_class(chain)
    api_key_env_var = {
        "etherscan": "ETHERSCAN_API_KEY",
        "basescan": "BASESCAN_API_KEY",
        "arbiscan": "ARBISCAN_API_KEY",
    }[chain]
    monkeypatch.delenv(api_key_env_var, raising=False)

    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    mocked_responses.add(
        responses.GET,
        mock_url,
        json={
            "result": [
                {
                    "hash": "0xabc",
                    "from": {"hash": "0x123"},
                    "to": {"hash": "0x456"},
                    "value": "100",
                    "timeStamp": "1672531200",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000",
                }
            ]
        },
        status=200,
    )

    transactions = adapter.get_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert len(mocked_responses.calls) == 1
    assert mocked_responses.calls[0].request.url == mock_url

# Mock JSON responses imitating the blockchain explorer API
MOCK_TRANSACTIONS_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": [
        {
            "hash": "0xtxhash1",
            "timeStamp": "1633027200",
            "from": {"hash": "0xfromaddress1"},
            "to": {"hash": "0xtoaddress1"},
            "value": "1000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "50000000000"
        },
        {
            "hash": "0xtxhash2",
            "timeStamp": "1633027201",
            "from": {"hash": "0xfromaddress2"},
            "to": {"hash": "0xtoaddress2"},
            "value": "2000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "50000000000"
        }
    ]
}

MOCK_TOKEN_TRANSFERS_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": [
        {
            "hash": "0xtokenhash1",
            "timeStamp": "1633027300",
            "from": {"hash": "0xfromaddress3"},
            "to": {"hash": "0xtoaddress3"},
            "total": {"value": "500"},
            "token": {"symbol": "TKN"},
            "tokenDecimal": "18"
        },
        {
            "hash": "0xtokenhash2",
            "timeStamp": "1633027301",
            "from": {"hash": "0xfromaddress4"},
            "to": {"hash": "0xtoaddress4"},
            "total": {"value": "1000"},
            "token": {"symbol": "MTK"},
            "tokenDecimal": "6"
        }
    ]
}

# Mock response with one valid and one invalid item (missing 'hash')
MOCK_INVALID_ITEM_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": [
        {
            "hash": "0xtxhash_valid",
            "timeStamp": "1633027200",
            "from": {"hash": "0xfromaddress_valid"},
            "to": {"hash": "0xtoaddress_valid"},
            "value": "1000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "50000000000"
        },
        {
            # Missing 'hash'
            "timeStamp": "1633027201",
            "from": {"hash": "0xfromaddress_invalid"},
            "to": {"hash": "0xtoaddress_invalid"},
            "value": "2000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "50000000000"
        }
    ]
}

# Mock response where the 'result' is not a list
MOCK_INVALID_RESULT_RESPONSE = {
    "status": "0",
    "message": "Error",
    "result": "Invalid API key"
}

DUMMY_ENDPOINT = "http://fake-api.com/data"

@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_parses_transactions_correctly(mock_get):
    """
    Verify that fetch_data correctly parses a successful transaction API response
    and returns a list of RawTransaction objects.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_TRANSACTIONS_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Act
    result = fetch_data(DUMMY_ENDPOINT, RawTransaction)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], RawTransaction)
    assert result[0].hash == "0xtxhash1"
    assert result[1].hash == "0xtxhash2"
    mock_get.assert_called_once_with(DUMMY_ENDPOINT, timeout=10)
    mock_response.raise_for_status.assert_called_once()

@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_parses_token_transfers_correctly(mock_get):
    """
    Verify that fetch_data correctly parses a successful token transfer API response
    and returns a list of RawTokenTransfer objects.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_TOKEN_TRANSFERS_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Act
    result = fetch_data(DUMMY_ENDPOINT, RawTokenTransfer)

    # Assert
    assert len(result) == 2
    assert isinstance(result[0], RawTokenTransfer)
    assert result[0].hash == "0xtokenhash1"
    assert result[0].token.symbol == "TKN"
    assert result[1].hash == "0xtokenhash2"
    assert result[1].token.symbol == "MTK"
    mock_get.assert_called_once_with(DUMMY_ENDPOINT, timeout=10)
    mock_response.raise_for_status.assert_called_once()

@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_handles_api_error_gracefully(mock_get):
    """
    Verify that fetch_data returns an empty list when the API call
    raises an exception (e.g., HTTPError).
    """
    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException("API is down")

    # Act
    result = fetch_data(DUMMY_ENDPOINT, RawTransaction)

    # Assert
    assert result == []
    mock_get.assert_called()

@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_handles_validation_error(mock_get, caplog):
    """
    Verify that fetch_data logs a warning for validation errors but continues
    processing other valid items in the response.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_INVALID_ITEM_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Act
    with caplog.at_level(logging.WARNING):
        result = fetch_data(DUMMY_ENDPOINT, RawTransaction)

    # Assert
    assert len(result) == 1
    assert result[0].hash == "0xtxhash_valid"
    assert "Validation error for item" in caplog.text


@patch('fetch_blockchain_data.requests.get')
def test_fetch_data_handles_invalid_result_format(mock_get, caplog):
    """
    Verify that fetch_data returns an empty list and logs an error when the
    API response's 'result' field is not a list.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_INVALID_RESULT_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Act
    with caplog.at_level(logging.ERROR):
        result = fetch_data(DUMMY_ENDPOINT, RawTransaction)

    # Assert
    assert result == []
    assert f"API response for {DUMMY_ENDPOINT} does not contain a list in 'result'" in caplog.text
