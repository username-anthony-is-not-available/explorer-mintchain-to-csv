
import logging
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from config import BASE_URL, TIMEOUT


def fetch_data(endpoint: str) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    current_endpoint: Optional[str] = endpoint

    while current_endpoint is not None:
        try:
            response = requests.get(current_endpoint, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                items = data.get('result')

                if isinstance(items, list):
                    all_items.extend(items)
                else:
                    # Log an error if 'result' is not a list
                    logging.error(f"API response for {current_endpoint} does not contain a list in 'result': {data}")
                    break

                next_page_params = data.get('next_page_params')
                if next_page_params:
                    # Construct the URL for the next page
                    url_parts = list(urlparse(current_endpoint))
                    query = dict(parse_qs(url_parts[4]))
                    query.update(next_page_params)
                    url_parts[4] = urlencode(query)
                    current_endpoint = urlunparse(url_parts)
                else:
                    # No more pages, exit the loop
                    current_endpoint = None
            else:
                logging.error(f"Error fetching data from {current_endpoint}: {response.status_code} - {response.text}")
                break
        except RequestException as e:
            logging.error(f"An error occurred while fetching data from {current_endpoint}: {str(e)}")
            break

    return all_items


# Function to fetch transactions
def fetch_transactions(wallet_address: str) -> List[Dict[str, Any]]:
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': wallet_address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
    }
    encoded_params = urlencode(params)
    url = f"{BASE_URL}?{encoded_params}"
    return fetch_data(url)


# Function to fetch token transfers
def fetch_token_transfers(wallet_address: str) -> List[Dict[str, Any]]:
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': wallet_address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
    }
    encoded_params = urlencode(params)
    url = f"{BASE_URL}?{encoded_params}"
    return fetch_data(url)


# Function to fetch internal transactions
def fetch_internal_transactions(wallet_address: str) -> List[Dict[str, Any]]:
    params = {
        'module': 'account',
        'action': 'txlistinternal',
        'address': wallet_address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
    }
    encoded_params = urlencode(params)
    url = f"{BASE_URL}?{encoded_params}"
    return fetch_data(url)
