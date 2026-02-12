import responses
import pytest
from explorer_adapters import MintchainAdapter
from models import RawTransaction
from config import EXPLORER_URLS

WALLET_ADDRESS = "0x1234567890123456789012345678901234567890"
CHAIN = "mintchain"

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_fetch_all_pages_pagination(mocked_responses):
    adapter = MintchainAdapter(CHAIN)
    base_url = EXPLORER_URLS[CHAIN]

    # Page 1: returns 10,000 items
    page1_results = [
        {
            "hash": f"0xhash1_{i}",
            "from": {"hash": "0x123"},
            "to": {"hash": WALLET_ADDRESS},
            "value": "100",
            "timeStamp": "1672531200",
            "gasUsed": "21000",
            "gasPrice": "1000000000",
        } for i in range(10000)
    ]

    mocked_responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&offset=10000&sort=asc&page=1",
        json={"status": "1", "message": "OK", "result": page1_results},
        status=200
    )

    # Page 2: returns 500 items
    page2_results = [
        {
            "hash": f"0xhash2_{i}",
            "from": {"hash": "0x123"},
            "to": {"hash": WALLET_ADDRESS},
            "value": "100",
            "timeStamp": "1672531300",
            "gasUsed": "21000",
            "gasPrice": "1000000000",
        } for i in range(500)
    ]

    mocked_responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlist&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&offset=10000&sort=asc&page=2",
        json={"status": "1", "message": "OK", "result": page2_results},
        status=200
    )

    transactions = adapter.get_transactions(WALLET_ADDRESS)

    assert len(transactions) == 10500
    assert transactions[0].hash == "0xhash1_0"
    assert transactions[9999].hash == "0xhash1_9999"
    assert transactions[10000].hash == "0xhash2_0"
    assert transactions[10499].hash == "0xhash2_499"

    assert len(mocked_responses.calls) == 2
