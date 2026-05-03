import pytest
import responses
from decimal import Decimal
from unittest.mock import patch
from price_service import get_token_price, get_defillama_price, _price_cache

@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps

def test_get_native_token_price(mocked_responses):
    _price_cache.clear()
    chain = "ethereum"
    timestamp = 1672531200  # 2023-01-01
    date_str = "01-01-2023"
    coin_id = "ethereum"

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}&localization=false"
    mocked_responses.add(
        responses.GET,
        url,
        json={
            "market_data": {
                "current_price": {"usd": 1200.50}
            }
        },
        status=200
    )

    price = get_token_price(chain, timestamp)
    assert price == Decimal("1200.5")
    assert len(mocked_responses.calls) == 1

    # Test caching
    price_cached = get_token_price(chain, timestamp)
    assert price_cached == Decimal("1200.5")
    assert len(mocked_responses.calls) == 1

def test_get_erc20_token_price(mocked_responses):
    _price_cache.clear()
    chain = "polygon"
    platform_id = "polygon-pos"
    contract_address = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174" # USDC on Polygon
    timestamp = 1672531200
    date_str = "01-01-2023"
    coin_id = "usd-coin"

    # Mock coin ID lookup
    mocked_responses.add(
        responses.GET,
        f"https://api.coingecko.com/api/v3/coins/{platform_id}/contract/{contract_address}",
        json={"id": coin_id},
        status=200
    )

    # Mock price lookup
    mocked_responses.add(
        responses.GET,
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}&localization=false",
        json={
            "market_data": {
                "current_price": {"usd": 1.0}
            }
        },
        status=200
    )

    price = get_token_price(chain, timestamp, contract_address=contract_address)
    assert price == Decimal("1.0")
    assert len(mocked_responses.calls) == 2

@patch("time.sleep", return_value=None)
def test_rate_limiting(mock_sleep, mocked_responses):
    _price_cache.clear()
    chain = "ethereum"
    timestamp = 1672531200
    date_str = "01-01-2023"
    coin_id = "ethereum"
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}&localization=false"

    # Add a 429 response followed by a 200 response
    mocked_responses.add(responses.GET, url, status=429)
    mocked_responses.add(
        responses.GET,
        url,
        json={"market_data": {"current_price": {"usd": 1200.50}}},
        status=200
    )

    price = get_token_price(chain, timestamp)
    assert price == Decimal("1200.5")
    assert len(mocked_responses.calls) == 2
    assert mock_sleep.call_count == 1

def test_cache_none_result(mocked_responses):
    _price_cache.clear()
    chain = "ethereum"
    timestamp = 1672531200
    date_str = "01-01-2023"
    coin_id = "ethereum"
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}&localization=false"

    # Mock a response that doesn't contain price data
    mocked_responses.add(
        responses.GET,
        url,
        json={"market_data": {}},
        status=200
    )

    price = get_token_price(chain, timestamp)
    assert price is None
    assert len(mocked_responses.calls) == 1

    # Second call should use cache (return None without another API call)
    price_cached = get_token_price(chain, timestamp)
    assert price_cached is None
    assert len(mocked_responses.calls) == 1

def test_get_defillama_native_price(mocked_responses):
    """Test fetching native coin price via DefiLlama."""
    _price_cache.clear()
    chain = "ethereum"
    timestamp = 1672531200  # 2023-01-01
    symbol = "ETH"
    token_id = "ethereum:0x0000000000000000000000000000000000000000"
    url = f"https://coins.llama.fi/prices/historical/{timestamp}"
    
    mocked_responses.add(
        responses.GET,
        url,
        json={
            "coins": {
                token_id: {"price": 1200.50}
            }
        },
        status=200,
        match_querystring=False
    )
    
    price = get_defillama_price(chain, timestamp, symbol=symbol)
    assert price == Decimal("1200.5")
    assert len(mocked_responses.calls) == 1

def test_get_defillama_token_price(mocked_responses):
    """Test fetching ERC-20 token price via DefiLlama."""
    _price_cache.clear()
    chain = "polygon"
    timestamp = 1672531200
    contract_address = "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"  # USDC on Polygon
    token_id = f"polygon-pos:{contract_address.lower()}"
    url = f"https://coins.llama.fi/prices/historical/{timestamp}"
    
    mocked_responses.add(
        responses.GET,
        url,
        json={
            "coins": {
                token_id: {"price": 1.0}
            }
        },
        status=200,
        match_querystring=False
    )
    
    price = get_defillama_price(chain, timestamp, contract_address=contract_address)
    assert price == Decimal("1.0")
    assert len(mocked_responses.calls) == 1

def test_get_token_price_defillama_source(mocked_responses):
    """Test get_token_price uses DefiLlama when source='defillama'."""
    _price_cache.clear()
    chain = "ethereum"
    timestamp = 1672531200
    symbol = "ETH"
    token_id = "ethereum:0x0000000000000000000000000000000000000000"
    url = f"https://coins.llama.fi/prices/historical/{timestamp}"
    
    mocked_responses.add(
        responses.GET,
        url,
        json={
            "coins": {
                token_id: {"price": 1200.50}
            }
        },
        status=200,
        match_querystring=False
    )
    
    price = get_token_price(chain, timestamp, symbol=symbol, source="defillama")
    assert price == Decimal("1200.5")
    assert len(mocked_responses.calls) == 1
