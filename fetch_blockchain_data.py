
import requests
from requests.exceptions import RequestException

from config import BASE_URL, TIMEOUT


# General function to fetch data from an API endpoint
def fetch_data(endpoint):
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
        else:
            print(f"Error fetching data from {endpoint}: {response.status_code} - {response.text}")
            return []
    except RequestException as e:
        print(f"An error occurred while fetching data from {endpoint}: {str(e)}")
        return []


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
