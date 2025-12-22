import logging
from typing import List, Type, TypeVar
import requests
from pydantic import ValidationError, BaseModel
from requests.exceptions import RequestException
from urllib.parse import urlencode

from config import BASE_URL, TIMEOUT
from models import RawTokenTransfer, RawTransaction

T = TypeVar('T', bound=BaseModel)

def fetch_data(endpoint: str, model: Type[T]) -> List[T]:
    try:
        response = requests.get(endpoint, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        result_list = data.get('result')
        if not isinstance(result_list, list):
            logging.error(f"API response for {endpoint} does not contain a list in 'result': {data}")
            return []

        validated_data: List[T] = []
        for item in result_list:
            try:
                validated_item = model.model_validate(item)
                validated_data.append(validated_item)
            except ValidationError as e:
                logging.warning(f"Validation error for item in {endpoint}: {e}. Item: {item}")

        return validated_data

    except RequestException as e:
        logging.error(f"An error occurred while fetching data from {endpoint}: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return []


# Function to fetch transactions
def fetch_transactions(wallet_address: str) -> List[RawTransaction]:
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
    return fetch_data(url, RawTransaction)


# Function to fetch token transfers
def fetch_token_transfers(wallet_address: str) -> List[RawTokenTransfer]:
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
    return fetch_data(url, RawTokenTransfer)


# Function to fetch internal transactions
def fetch_internal_transactions(wallet_address: str) -> List[RawTransaction]:
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
    return fetch_data(url, RawTransaction)
