import responses
import logging
from explorer_adapters import MintchainAdapter
from models import RawTransaction

WALLET_ADDRESS = "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a"
CHAIN = "mintchain"

@responses.activate
def test_mintchain_internal_transactions_with_items_and_raw_addresses():
    adapter = MintchainAdapter(CHAIN)
    base_url = "https://api.routescan.io/v2/network/mainnet/evm/185/etherscan"
    mock_url = f"{base_url}?module=account&action=txlistinternal&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    # Mocking the Routescan V2 response structure
    mock_response = {
        "status": "1",
        "message": "OK",
        "result": [
            {
                "hash": "0xd49029e9e815284a1395d834924df6c2ed457a8b9689ab5a35ddb422ac4eb076",
                "timeStamp": "1718770339",
                "from": "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a",
                "to": "0x4200000000000000000000000000000000000006",
                "value": "1000000000000000",
                "gas": "36762"
            }
        ]
    }

    responses.add(responses.GET, mock_url, json=mock_response, status=200)

    internal_txs = adapter.get_internal_transactions(WALLET_ADDRESS)

    assert len(internal_txs) == 1
    assert internal_txs[0].hash == "0xd49029e9e815284a1395d834924df6c2ed457a8b9689ab5a35ddb422ac4eb076"
    assert internal_txs[0].from_address.hash == "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a"
    assert internal_txs[0].to_address.hash == "0x4200000000000000000000000000000000000006"
    assert internal_txs[0].gasUsed == "36762"

@responses.activate
def test_mintchain_internal_transactions_with_items_key():
    adapter = MintchainAdapter(CHAIN)
    base_url = "https://api.routescan.io/v2/network/mainnet/evm/185/etherscan"
    mock_url = f"{base_url}?module=account&action=txlistinternal&address={WALLET_ADDRESS}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    # Mocking the Routescan V2 response structure with 'items' instead of 'result'
    mock_response = {
        "status": "1",
        "message": "OK",
        "items": [
            {
                "hash": "0xd49029e9e815284a1395d834924df6c2ed457a8b9689ab5a35ddb422ac4eb076",
                "timeStamp": "1718770339",
                "from": "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a",
                "to": "0x4200000000000000000000000000000000000006",
                "value": "1000000000000000",
                "gas": "36762"
            }
        ]
    }

    responses.add(responses.GET, mock_url, json=mock_response, status=200)

    internal_txs = adapter.get_internal_transactions(WALLET_ADDRESS)

    assert len(internal_txs) == 1
    assert internal_txs[0].hash == "0xd49029e9e815284a1395d834924df6c2ed457a8b9689ab5a35ddb422ac4eb076"
    assert internal_txs[0].from_address.hash == "0xe55b0367a178d9cf5f03354fd06904a8b3bb682a"
    assert internal_txs[0].gasUsed == "36762"
