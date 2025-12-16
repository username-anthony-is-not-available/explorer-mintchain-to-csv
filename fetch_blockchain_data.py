
import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from config import BASE_URL, TIMEOUT


# General function to fetch data from an API endpoint
def fetch_data(endpoint):
    all_items = []
    current_url = endpoint

    parsed_endpoint = urlparse(endpoint)
    base_endpoint = urlunparse(
        (parsed_endpoint.scheme, parsed_endpoint.netloc, parsed_endpoint.path, '', '', '')
    )
    original_params = parse_qs(parsed_endpoint.query)

    while current_url:
        try:
            response = requests.get(current_url, timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                all_items.extend(items)

                next_page_params = data.get('next_page_params')
                if next_page_params:
                    # Create a new dictionary for the next page's parameters
                    query_params = {}
                    # Add original parameters first
                    query_params.update(original_params)
                    # Now update with the next_page_params, which will overwrite
                    # any pagination-related keys (like 'page' or 'offset')
                    query_params.update(next_page_params)

                    params = urlencode(query_params, doseq=True)
                    current_url = f"{base_endpoint}?{params}"
                else:
                    current_url = None
            else:
                print(f"Error fetching data from {current_url}: {response.status_code} - {response.text}")
                current_url = None
        except RequestException as e:
            print(f"An error occurred while fetching data from {current_url}: {str(e)}")
            current_url = None

    return all_items


# Function to fetch transactions
def fetch_transactions(wallet_address):
    url = f'{BASE_URL}{wallet_address}/transactions'
    return fetch_data(url)


# Function to fetch token transfers
def fetch_token_transfers(wallet_address):
    url = f'{BASE_URL}{wallet_address}/token-transfers'
    return fetch_data(url)


# Function to fetch internal transactions
def fetch_internal_transactions(wallet_address):
    url = f'{BASE_URL}{wallet_address}/internal-transactions'
    return fetch_data(url)
