import logging
from typing import List, Type, TypeVar
import requests
from pydantic import ValidationError, BaseModel
from requests.exceptions import RequestException, HTTPError
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError, retry_if_exception_type
from urllib.parse import urlencode

from config import BASE_URL, TIMEOUT
from models import RawTokenTransfer, RawTransaction

T = TypeVar('T', bound=BaseModel)

def wait_retry_after_or_exponential(retry_state):
    """
    A custom wait strategy that checks for a 'Retry-After' header in the
    exception if it's a 429 HTTPError, otherwise falls back to exponential backoff.
    """
    exception = retry_state.outcome.exception()
    if isinstance(exception, HTTPError) and exception.response.status_code == 429:
        retry_after = exception.response.headers.get("Retry-After")
        if retry_after:
            try:
                wait_seconds = int(retry_after)
                logging.warning(f"Rate limit exceeded. Retrying after {wait_seconds} seconds.")
                return wait_seconds
            except (ValueError, TypeError):
                logging.warning(f"Could not parse 'Retry-After' header: {retry_after}. Falling back to exponential backoff.")

    return wait_exponential(multiplier=1, min=4, max=60)(retry_state)

def _log_and_return_empty(retry_state):
    logging.error(f"An error occurred while fetching data after multiple retries: {retry_state.outcome.exception()}")
    return []

@retry(
    stop=stop_after_attempt(5),
    wait=wait_retry_after_or_exponential,
    retry_error_callback=_log_and_return_empty,
    retry=retry_if_exception_type(RequestException)
)
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

    except Exception as e:
        if isinstance(e, RequestException):
            raise  # Reraise RequestException to be handled by tenacity
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
