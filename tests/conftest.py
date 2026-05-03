import pytest
import os
from cache_manager import cache_manager

@pytest.fixture(autouse=True)
def disable_persistent_cache(monkeypatch):
    """
    Automatically disables the persistent cache for all tests to prevent interference.
    """
    monkeypatch.setenv("DISABLE_CACHE", "true")
