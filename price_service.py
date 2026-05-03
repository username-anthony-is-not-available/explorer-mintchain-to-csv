import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, Optional, Union
from decimal import Decimal

from config import (
    COINGECKO_BASE_URL, COINGECKO_PLATFORM_MAP, TIMEOUT, NATIVE_CURRENCIES,
    DEFILLAMA_BASE_URL, DEFILLAMA_COIN_MAP, DEFILLAMA_PLATFORM_MAP
)
from fetch_blockchain_data import session

# Cache for token prices to avoid redundant API calls and respect rate limits
# Key format: "platform:contract_address:timestamp_day" for tokens
# Key format: "coin_id:timestamp_day" for native coins
_price_cache: Dict[str, Optional[Decimal]] = {}

def get_defillama_price(
    chain: str,
    timestamp: int,
    contract_address: Optional[str] = None,
    symbol: Optional[str] = None
) -> Optional[Decimal]:
    """
    Fetches historical price via DefiLlama API.
    For tokens: uses {platform}:{contract_address} format.
    For native coins: uses {coin_id}:0x0000000000000000000000000000000000000000.
    """
    if contract_address:
        platform = DEFILLAMA_PLATFORM_MAP.get(chain)
        if not platform:
            logging.warning(f"No DefiLlama platform ID for chain: {chain}")
            return None
        token_id = f"{platform}:{contract_address.lower()}"
    else:
        lookup_symbol = symbol.upper() if symbol else NATIVE_CURRENCIES.get(chain, "ETH").upper()
        coin_id = DEFILLAMA_COIN_MAP.get(lookup_symbol)
        if not coin_id:
            logging.warning(f"No DefiLlama coin ID for symbol: {lookup_symbol}")
            return None
        token_id = f"{coin_id}:0x0000000000000000000000000000000000000000"

    url = f"{DEFILLAMA_BASE_URL}/prices/historical/{timestamp}"
    params = {"tokens": token_id}

    try:
        response = session.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        coins = data.get("coins", {})
        token_data = coins.get(token_id)
        if token_data:
            price = token_data.get("price")
            if price is not None:
                return Decimal(str(price))
        return None
    except Exception as e:
        logging.error(f"Error fetching DefiLlama price for {token_id} at {timestamp}: {e}")
        return None


def get_token_price(
    chain: str,
    timestamp: int,
    contract_address: Optional[str] = None,
    symbol: Optional[str] = None,
    source: str = "coingecko"
) -> Optional[Decimal]:
    """
    Fetches the historical price of a token or native coin.
    
    Args:
        chain: The blockchain name (e.g., 'ethereum', 'polygon', 'mintchain').
        timestamp: Unix timestamp of the transaction.
        contract_address: The contract address of the token (None for native currency).
        symbol: The symbol of the token (used for native currency lookup).
        source: Price source, either "coingecko" or "defillama".
    
    Returns:
        The price in USD as a Decimal, or None if not found.
    """
    if source == "defillama":
        return get_defillama_price(chain, timestamp, contract_address, symbol)
    else:
        return _get_coingecko_price(chain, timestamp, contract_address, symbol)

def _get_coingecko_price(
    chain: str,
    timestamp: int,
    contract_address: Optional[str] = None,
    symbol: Optional[str] = None
) -> Optional[Decimal]:
    """Fetches historical price from Coingecko (original logic)."""
    date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%d-%m-%Y")
    platform_id = COINGECKO_PLATFORM_MAP.get(chain)

    if contract_address:
        if not platform_id:
            logging.warning(f"No Coingecko platform ID for chain: {chain}")
            return None
        cache_key = f"{platform_id}:{contract_address.lower()}:{date_str}"
        if cache_key in _price_cache:
            return _price_cache[cache_key]
        price = _fetch_price_by_contract(platform_id, contract_address, date_str)
        _price_cache[cache_key] = price
        return price
    else:
        lookup_symbol = symbol.upper() if symbol else NATIVE_CURRENCIES.get(chain, "ETH").upper()
        coin_id = _get_coin_id_by_symbol(lookup_symbol)
        if not coin_id:
            logging.warning(f"No Coingecko coin ID for symbol: {lookup_symbol}")
            return None
        cache_key = f"{coin_id}:{date_str}"
        if cache_key in _price_cache:
            return _price_cache[cache_key]
        price = _fetch_price_by_coin_id(coin_id, date_str)
        _price_cache[cache_key] = price
        return price

def _get_coin_id_by_symbol(symbol: str) -> Optional[str]:
    """Maps a native currency symbol to a Coingecko coin ID."""
    mapping = {
        "ETH": "ethereum",
        "MATIC": "matic-network",
        "BNB": "binancecoin",
        "ARB": "arbitrum",
        "OP": "optimism",
    }
    return mapping.get(symbol.upper())

def _fetch_price_by_contract(platform_id: str, contract_address: str, date_str: str) -> Optional[Decimal]:
    """Fetches historical price using Coingecko's /coins/{id}/contract/{contract_address}/history endpoint."""
    coin_id = _get_coin_id_from_contract(platform_id, contract_address)
    if not coin_id:
        return None
    return _fetch_price_by_coin_id(coin_id, date_str)

def _get_coin_id_from_contract(platform_id: str, contract_address: str) -> Optional[str]:
    """Finds the Coingecko coin ID for a given contract address on a platform."""
    url = f"{COINGECKO_BASE_URL}/coins/{platform_id}/contract/{contract_address.lower()}"
    api_key = os.getenv("COINGECKO_API_KEY")
    headers = {"x-cg-demo-api-key": api_key} if api_key else {}

    try:
        response = session.get(url, headers=headers, timeout=TIMEOUT)
        if response.status_code == 429:
            logging.warning("Coingecko rate limit exceeded. Sleeping for 30 seconds.")
            time.sleep(30)
            return _get_coin_id_from_contract(platform_id, contract_address)

        response.raise_for_status()
        data = response.json()
        return data.get("id")
    except Exception as e:
        logging.error(f"Error fetching coin ID for {contract_address} on {platform_id}: {e}")
        return None

def _fetch_price_by_coin_id(coin_id: str, date_str: str) -> Optional[Decimal]:
    """Fetches historical price using Coingecko's /coins/{id}/history endpoint."""
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/history"
    params = {"date": date_str, "localization": "false"}
    api_key = os.getenv("COINGECKO_API_KEY")
    headers = {"x-cg-demo-api-key": api_key} if api_key else {}

    try:
        response = session.get(url, params=params, headers=headers, timeout=TIMEOUT)
        if response.status_code == 429:
            logging.warning("Coingecko rate limit exceeded. Sleeping for 30 seconds.")
            time.sleep(30)
            return _fetch_price_by_coin_id(coin_id, date_str)

        response.raise_for_status()
        data = response.json()

        market_data = data.get("market_data")
        if market_data:
            current_price = market_data.get("current_price")
            if current_price:
                usd_price = current_price.get("usd")
                if usd_price is not None:
                    return Decimal(str(usd_price))
        return None
    except Exception as e:
        logging.error(f"Error fetching price for {coin_id} on {date_str}: {e}")
        return None
