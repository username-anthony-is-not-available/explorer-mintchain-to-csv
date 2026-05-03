import responses
import pytest
from main import process_transactions
from explorer_adapters import MintchainAdapter
from config import EXPLORER_URLS

@responses.activate
def test_mock_mintchain_full_cycle():
    # Mocking a full MintChain transaction cycle
    wallet_address = "0xmockwallet"
    chain = "mintchain"
    base_url = EXPLORER_URLS[chain]

    # 1. Mock txlist
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "hash": "0x1",
                    "timeStamp": "1704067200",
                    "from": {"hash": wallet_address},
                    "to": {"hash": "0xother"},
                    "value": "1000000000000000000",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000"
                }
            ]
        },
        status=200
    )

    # 2. Mock tokentx
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"status": "1", "message": "OK", "result": []},
        status=200
    )

    # 3. Mock txlistinternal
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlistinternal&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"status": "1", "message": "OK", "result": []},
        status=200
    )
    
    # 4. Mock tokennfttx
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=tokennfttx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"status": "1", "message": "OK", "result": []},
        status=200
    )
    
    # 5. Mock token1155tx
    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=token1155tx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        json={"status": "1", "message": "OK", "result": []},
        status=200
    )

    transactions = process_transactions(wallet_address, chain)
    
    assert len(transactions) == 1
    assert transactions[0].tx_hash == "0x1"
    assert transactions[0].sent_amount == "1"
    assert transactions[0].sent_currency == "ETH"
    assert transactions[0].fee_amount == "0.000021"

@responses.activate
def test_mock_explorer_error_handling():
    # Test how the system handles an API error (e.g. 500)
    wallet_address = "0xmockwallet"
    chain = "etherscan"
    base_url = EXPLORER_URLS[chain]

    responses.add(
        responses.GET,
        f"{base_url}?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000",
        status=500
    )
    # Mock others as empty
    for action in ["tokentx", "txlistinternal", "tokennfttx", "token1155tx"]:
        responses.add(responses.GET, f"{base_url}?module=account&action={action}&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000", json={"result": []}, status=200)

    # process_transactions should handle the error and return an empty list or partial list
    transactions = process_transactions(wallet_address, chain)
    assert isinstance(transactions, list)
