
import logging
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from config import BASE_URL, TIMEOUT


# General function to fetch data from an API endpoint
def fetch_data(endpoint: str) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    current_url: Optional[str] = endpoint

    parsed_endpoint = urlparse(endpoint)
    base_endpoint: str = urlunparse(
        (parsed_endpoint.scheme, parsed_endpoint.netloc, parsed_endpoint.path, '', '', '')
    )
    original_params: Dict[str, List[str]] = parse_qs(parsed_endpoint.query)

    while current_url:
        try:
            response = requests.get(current_url, timeout=TIMEOUT)
            if response.status_code == 200:
                data: Dict[str, Any] = response.json()
                items: List[Dict[str, Any]] = data.get('items', [])
                all_items.extend(items)

                next_page_params: Optional[Dict[str, Any]] = data.get('next_page_params')
                if next_page_params:
                    # Create a new dictionary for the next page's parameters
                    query_params: Dict[str, Any] = {}
                    # Add original parameters first
                    query_params.update(original_params)
                    # Now update with the next_page_params, which will overwrite
                    # any pagination-related keys (like 'page' or 'offset')
                    query_params.update(next_page_params)

                    params: str = urlencode(query_params, doseq=True)
                    current_url = f"{base_endpoint}?{params}"
                else:
                    current_url = None
            else:
                logging.error(f"Error fetching data from {current_url}: {response.status_code} - {response.text}")
                current_url = None
        except RequestException as e:
            logging.error(f"An error occurred while fetching data from {current_url}: {str(e)}")
            current_url = None

    return all_items


# Function to fetch transactions
def fetch_transactions(wallet_address: str) -> List[Dict[str, Any]]:
    url: str = f'{BASE_URL}{wallet_address}/transactions'
    return fetch_data(url)


# Function to fetch token transfers
def fetch_token_transfers(wallet_address: str) -> List[Dict[str, Any]]:
    url: str = f'{BASE_URL}{wallet_address}/token-transfers'
    return fetch_data(url)


# Function to fetch internal transactions
def fetch_internal_transactions(wallet_address: str) -> List[Dict[str, Any]]:
    url: str = f'{BASE_URL}{wallet_address}/internal-transactions'
    return fetch_data(url)
