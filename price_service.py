import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional, Union
from decimal import Decimal

from config import COINGECKO_BASE_URL, COINGECKO_PLATFORM_MAP, TIMEOUT, NATIVE_CURRENCIES
from fetch_blockchain_data import session

# Cache for token prices to avoid redundant API calls and respect rate limits
# Key format: "platform:contract_address:timestamp_day" for tokens
# Key format: "coin_id:timestamp_day" for native coins
_price_cache: Dict[str, Optional[Decimal]] = {}

def get_token_price(
    chain: str,
    timestamp: int,
    contract_address: Optional[str] = None,
    symbol: Optional[str] = None
) -> Optional[Decimal]:
    """
    Fetches the historical price of a token or native coin from Coingecko.

    Args:
        chain: The blockchain name (e.g., 'ethereum', 'polygon', 'mintchain').
        timestamp: Unix timestamp of the transaction.
        contract_address: The contract address of the token (None for native currency).
        symbol: The symbol of the token (used for native currency lookup).

    Returns:
        The price in USD as a Decimal, or None if not found.
    """
    # Convert timestamp to YYYY-MM-DD for Coingecko's historical API
    date_str = datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y")

    platform_id = COINGECKO_PLATFORM_MAP.get(chain)

    if contract_address:
        # ERC-20 token price by contract address
        if not platform_id:
            logging.warning(f"No Coingecko platform ID found for chain: {chain}")
            return None

        cache_key = f"{platform_id}:{contract_address.lower()}:{date_str}"
        if cache_key in _price_cache:
            return _price_cache[cache_key]

        price = _fetch_price_by_contract(platform_id, contract_address, date_str)
        _price_cache[cache_key] = price
        return price
    else:
        # Native currency price
        lookup_symbol = symbol.upper() if symbol else NATIVE_CURRENCIES.get(chain, "ETH").upper()
        coin_id = _get_coin_id_by_symbol(lookup_symbol)

        if not coin_id:
            logging.warning(f"No Coingecko coin ID found for symbol: {lookup_symbol}")
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
    # Note: Coingecko's public API for historical contract price is a bit tricky.
    # Usually, we first need to find the coin ID by contract address.
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
