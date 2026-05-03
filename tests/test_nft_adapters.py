import responses
from explorer_adapters import MintchainAdapter
from config import EXPLORER_URLS

def test_get_nft_transfers_success():
    chain = "mintchain"
    adapter = MintchainAdapter(chain)
    wallet_address = "0x123"
    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=account&action=tokennfttx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            mock_url,
            json={
                "status": "1",
                "message": "OK",
                "result": [
                    {
                        "hash": "0xnft",
                        "timeStamp": "1672531200",
                        "from": {"hash": "0xfrom"},
                        "to": {"hash": "0xto"},
                        "tokenID": "1",
                        "tokenName": "NFT Name",
                        "tokenSymbol": "NFT",
                    }
                ],
            },
            status=200,
        )

        transfers = adapter.get_nft_transfers(wallet_address)
        assert len(transfers) == 1
        assert transfers[0].hash == "0xnft"
        assert transfers[0].tokenSymbol == "NFT"

def test_get_1155_transfers_success():
    chain = "mintchain"
    adapter = MintchainAdapter(chain)
    wallet_address = "0x123"
    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=account&action=token1155tx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            mock_url,
            json={
                "status": "1",
                "message": "OK",
                "result": [
                    {
                        "hash": "0x1155",
                        "timeStamp": "1672531200",
                        "from": {"hash": "0xfrom"},
                        "to": {"hash": "0xto"},
                        "tokenID": "1",
                        "tokenValue": "10",
                        "tokenName": "1155 Name",
                        "tokenSymbol": "1155",
                    }
                ],
            },
            status=200,
        )

        transfers = adapter.get_1155_transfers(wallet_address)
        assert len(transfers) == 1
        assert transfers[0].hash == "0x1155"
        assert transfers[0].tokenValue == "10"

def test_get_nft_transfers_with_items_key():
    chain = "mintchain"
    adapter = MintchainAdapter(chain)
    wallet_address = "0x123"
    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=account&action=tokennfttx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&page=1&offset=10000"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            mock_url,
            json={
                "status": "1",
                "message": "OK",
                "items": [
                    {
                        "hash": "0xnft_items",
                        "timeStamp": "1672531200",
                        "from": {"hash": "0xfrom"},
                        "to": {"hash": "0xto"},
                        "tokenID": "1",
                        "tokenName": "NFT Items",
                        "tokenSymbol": "NFTI",
                    }
                ],
            },
            status=200,
        )

        transfers = adapter.get_nft_transfers(wallet_address)
        assert len(transfers) == 1
        assert transfers[0].hash == "0xnft_items"
        assert transfers[0].tokenSymbol == "NFTI"
