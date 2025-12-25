import pytest
import responses
from unittest.mock import patch, call
import logging
from requests.exceptions import RequestException, HTTPError

from fetch_blockchain_data import fetch_data, fetch_transactions, fetch_token_transfers, fetch_internal_transactions
from config import BASE_URL
from models import RawTransaction

WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_fetch_transactions_success(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"result": [{
            "hash": "0xabc",
            "from": {"hash": "0x123"},
            "to": {"hash": "0x456"},
            "value": "100",
            "timeStamp": "1672531200",
            "gasUsed": "21000",
            "gasPrice": "1000000000"
        }]},
        status=200,
    )
    transactions = fetch_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert transactions[0].hash == "0xabc"

def test_fetch_transactions_failure(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(responses.GET, mock_url, status=500)
    transactions = fetch_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0

def test_fetch_transactions_validation_error(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"result": [{"hash": "0xabc"}]},  # Missing required fields
        status=200,
    )
    transactions = fetch_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0

def test_fetch_transactions_malformed_response(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"data": "not a result list"}, # Malformed response
        status=200,
    )
    transactions = fetch_transactions(WALLET_ADDRESS)
    assert len(transactions) == 0

def test_fetch_token_transfers_success(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=tokentx&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"result": [{
            "hash": "0xdef",
            "from": {"hash": "0x123"},
            "to": {"hash": "0x456"},
            "timeStamp": "1672531201",
            "total": {"value": "200"},
            "token": {"symbol": "TKN"}
        }]},
        status=200,
    )
    transfers = fetch_token_transfers(WALLET_ADDRESS)
    assert len(transfers) == 1
    assert transfers[0].hash == "0xdef"

def test_fetch_internal_transactions_success(mocked_responses):
    mock_url = f"{BASE_URL}?module=account&action=txlistinternal&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"
    mocked_responses.add(
        responses.GET,
        mock_url,
        json={"result": [{
            "hash": "0xghi",
            "from": {"hash": "0x123"},
            "to": {"hash": "0x456"},
            "value": "300",
            "timeStamp": "1672531202",
            "gasUsed": "21000",
            "gasPrice": "1000000000"
        }]},
        status=200,
    )
    transactions = fetch_internal_transactions(WALLET_ADDRESS)
    assert len(transactions) == 1
    assert transactions[0].hash == "0xghi"

@patch('requests.get')
def test_fetch_data_retry_logic(mock_get, caplog):
    # Configure the mock to raise a RequestException 5 times
    mock_get.side_effect = RequestException("Test Exception")

    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

    with caplog.at_level(logging.ERROR):
        result = fetch_data(mock_url, RawTransaction)

    # Check that the function was called 5 times
    assert mock_get.call_count == 5

    # Check that the result is an empty list
    assert result == []

    # Check that the error was logged
    assert "An error occurred while fetching data after multiple retries" in caplog.text

@patch('time.sleep', return_value=None)
@responses.activate
def test_fetch_data_rate_limiting_logic(mock_sleep, caplog):
    # Configure the mock to return a 429 error with a Retry-After header
    mock_url = f"{BASE_URL}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc"

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
    mock_sleep.assert_has_calls([call(10)] * 4)

    # Check that the warning was logged
    assert "Rate limit exceeded. Retrying after 10 seconds." in caplog.text

    # Check that the final error was logged
    assert "An error occurred while fetching data after multiple retries" in caplog.text

    # Check that the result is an empty list
    assert result == []
