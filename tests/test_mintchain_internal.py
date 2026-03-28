import pytest
import responses
from explorer_adapters import MintchainAdapter
from models import RawTransaction
from config import EXPLORER_URLS

@responses.activate
def test_mintchain_internal_transactions_v2_support():
    # Mock a response from Routescan V2 styled API
    chain = "mintchain"
    wallet_address = "0xwallet"
    base_url = EXPLORER_URLS[chain]

    # Standard Etherscan-compatible internal transaction URL
    mock_url = f"{base_url}?module=account&action=txlistinternal&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    responses.add(
        responses.GET,
        mock_url,
        json={
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "transactionHash": "0xinternal1",
                    "timeStamp": "1710000000",
                    "from": "0xfrom",
                    "to": "0xto",
                    "value": "1000000000000000000",
                    "gas": "21000"
                }
            ]
        },
        status=200
    )

    adapter = MintchainAdapter(chain)
    internal_txs = adapter.get_internal_transactions(wallet_address)

    assert len(internal_txs) == 1
    assert internal_txs[0].hash == "0xinternal1"
    assert internal_txs[0].from_address.hash == "0xfrom"
    assert internal_txs[0].gasUsed == "21000"

@responses.activate
def test_fetch_data_v2_items_key_support():
    # Test support for 'items' key instead of 'result'
    from fetch_blockchain_data import fetch_data

    mock_url = "http://fake-api.com/v2/items"
    responses.add(
        responses.GET,
        mock_url,
        json={
            "items": [
                {
                    "hash": "0xitem1",
                    "timeStamp": "1710000000",
                    "from": "0xfrom",
                    "to": "0xto",
                    "value": "500000000000000000"
                }
            ]
        },
        status=200
    )

    data = fetch_data(mock_url, RawTransaction)
    assert len(data) == 1
    assert data[0].hash == "0xitem1"
    assert data[0].gasUsed is None
