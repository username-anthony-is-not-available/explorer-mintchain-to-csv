import pytest
import responses
from fetch_blockchain_data import fetch_transactions, fetch_token_transfers, fetch_internal_transactions
from config import BASE_URL

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
