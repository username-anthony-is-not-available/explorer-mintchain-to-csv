import responses
from explorer_adapters import MintchainAdapter
from config import EXPLORER_URLS

from explorer_adapters import EtherscanAdapter

def test_get_block_number_by_timestamp_caching():
    EtherscanAdapter._block_cache.clear()
    chain = "mintchain"
    adapter = MintchainAdapter(chain)
    timestamp = 1725148800
    closest = "before"
    base_url = EXPLORER_URLS[chain]
    mock_url = f"{base_url}?module=block&action=getblocknobytime&timestamp={timestamp}&closest={closest}"

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            mock_url,
            json={"status": "1", "message": "OK", "result": "12345"},
            status=200,
        )

        # First call - should hit the API
        block1 = adapter.get_block_number_by_timestamp(timestamp, closest)
        assert block1 == 12345
        assert len(rsps.calls) == 1

        # Second call - should hit the cache
        block2 = adapter.get_block_number_by_timestamp(timestamp, closest)
        assert block2 == 12345
        assert len(rsps.calls) == 1  # Still 1 call

def test_get_block_number_by_timestamp_cache_isolation():
    EtherscanAdapter._block_cache.clear()
    chain = "mintchain"
    adapter = MintchainAdapter(chain)
    timestamp = 1725148800
    base_url = EXPLORER_URLS[chain]

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"{base_url}?module=block&action=getblocknobytime&timestamp={timestamp}&closest=before",
            json={"status": "1", "message": "OK", "result": "12345"},
            status=200,
        )
        rsps.add(
            responses.GET,
            f"{base_url}?module=block&action=getblocknobytime&timestamp={timestamp}&closest=after",
            json={"status": "1", "message": "OK", "result": "12346"},
            status=200,
        )

        # Different 'closest' parameter should result in different cache keys
        block_before = adapter.get_block_number_by_timestamp(timestamp, "before")
        block_after = adapter.get_block_number_by_timestamp(timestamp, "after")

        assert block_before == 12345
        assert block_after == 12346
        assert len(rsps.calls) == 2
