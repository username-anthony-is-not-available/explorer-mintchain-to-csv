import pytest
from api_key_manager import api_key_manager
from explorer_adapters import EtherscanAdapter


@pytest.fixture(autouse=True)
def reset_manager():
    api_key_manager.reset()
    yield
    api_key_manager.reset()


def test_adapter_api_key_rotation():
    api_key_manager.set_keys("etherscan", ["key_a", "key_b"])
    adapter = EtherscanAdapter(chain="etherscan")

    assert adapter.get_api_key() == "key_a"
    url1 = adapter._get_explorer_api_url({"module": "account", "action": "txlist"})
    assert "apikey=key_a" in url1

    # Rotate key
    next_key = adapter.rotate_api_key()
    assert next_key == "key_b"
    url2 = adapter._get_explorer_api_url({"module": "account", "action": "txlist"})
    assert "apikey=key_b" in url2


def test_adapter_api_key_invalidation():
    api_key_manager.set_keys("etherscan", ["bad_key", "good_key"])
    adapter = EtherscanAdapter(chain="etherscan")

    assert adapter.get_api_key() == "bad_key"
    adapter.invalidate_api_key("bad_key", reason="Invalid API Key")

    assert adapter.get_api_key() == "good_key"
    url = adapter._get_explorer_api_url({"module": "account", "action": "txlist"})
    assert "apikey=good_key" in url
