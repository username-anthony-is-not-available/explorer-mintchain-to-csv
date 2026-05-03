import responses
import pytest
import os
from fetch_blockchain_data import fetch_data
from models import RawTransaction
from cache_manager import cache_manager

def test_fetch_data_persistent_caching(tmp_path, monkeypatch):
    # Re-enable cache for this test
    monkeypatch.setenv("DISABLE_CACHE", "false")
    # Setup a fresh cache for testing
    cache_db = os.path.join(tmp_path, "test_cache.db")
    cache_manager.db_path = cache_db
    cache_manager._init_db()
    
    mock_url = "https://api.test.com/cached"
    mock_response = {
        "status": "1",
        "message": "OK",
        "result": [
            {
                "hash": "0x1",
                "timeStamp": "1704067200",
                "from": "0xwallet",
                "to": "0xother",
                "value": "1000",
                "gasUsed": "21000",
                "gasPrice": "1000"
            }
        ]
    }

    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, mock_url, json=mock_response, status=200)

        # First call - should hit the network and populate cache
        data1 = fetch_data(mock_url, RawTransaction)
        assert len(data1) == 1
        assert len(rsps.calls) == 1
        
        # Second call - should hit the cache (no network call)
        data2 = fetch_data(mock_url, RawTransaction)
        assert len(data2) == 1
        assert len(rsps.calls) == 1  # Still 1 network call
        
    # Verify the database file exists
    assert os.path.exists(cache_db)
