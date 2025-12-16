
import logging
from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from config import BASE_URL, TIMEOUT


def fetch_data(endpoint: str) -> List[Dict[str, Any]]:
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            # The API returns a dictionary with a 'result' key
            # that contains the list of transactions.
            if isinstance(data.get('result'), list):
                return data['result']
            else:
                logging.error(f"API response for {endpoint} does not contain a list in 'result': {data}")
                return []
        else:
            logging.error(f"Error fetching data from {endpoint}: {response.status_code} - {response.text}")
            return []
    except RequestException as e:
        logging.error(f"An error occurred while fetching data from {endpoint}: {str(e)}")
        return []


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
