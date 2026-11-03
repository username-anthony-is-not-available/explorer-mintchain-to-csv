import concurrent.futures
import os
import pytest
from api_key_manager import APIKeyManager


@pytest.fixture
def manager():
    return APIKeyManager()


def test_single_key(manager):
    manager.set_keys("etherscan", ["key1"])
    assert manager.get_key("etherscan") == "key1"
    # Consecutive calls without rotate=True return same key
    assert manager.get_key("etherscan") == "key1"


def test_round_robin_rotation(manager):
    manager.set_keys("etherscan", ["key1", "key2", "key3"])
    assert manager.get_key("etherscan") == "key1"
    assert manager.rotate_key("etherscan") == "key2"
    assert manager.rotate_key("etherscan") == "key3"
    assert manager.rotate_key("etherscan") == "key1"


def test_key_invalidation(manager):
    manager.set_keys("basescan", ["k1", "k2", "k3"])
    assert manager.get_key("basescan") == "k1"

    manager.invalidate_key("basescan", "k1", reason="429 rate limited or invalid")
    assert "k1" in manager.get_invalidated_keys("basescan")
    assert manager.get_active_keys("basescan") == ["k2", "k3"]

    # Active key should now be k2
    assert manager.get_key("basescan") == "k2"
    assert manager.rotate_key("basescan") == "k3"
    assert manager.rotate_key("basescan") == "k2"


def test_invalidate_all_keys(manager):
    manager.set_keys("polygon", ["p1", "p2"])
    manager.invalidate_key("polygon", "p1")
    manager.invalidate_key("polygon", "p2")

    assert manager.get_key("polygon") is None
    assert manager.rotate_key("polygon") is None
    assert manager.get_active_keys("polygon") == []


def test_environment_variable_loading(monkeypatch, manager):
    monkeypatch.setenv("ETHERSCAN_API_KEY", "env_key1, env_key2, env_key3")
    manager.register_env_mapping("etherscan", "ETHERSCAN_API_KEY")

    assert manager.get_active_keys("etherscan") == ["env_key1", "env_key2", "env_key3"]
    assert manager.get_key("etherscan") == "env_key1"
    assert manager.rotate_key("etherscan") == "env_key2"


def test_thread_safety(manager):
    manager.set_keys("thread_test", [f"key_{i}" for i in range(10)])

    def worker():
        for _ in range(100):
            k = manager.rotate_key("thread_test")
            assert k is not None

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker) for _ in range(5)]
        for f in concurrent.futures.as_completed(futures):
            f.result()
