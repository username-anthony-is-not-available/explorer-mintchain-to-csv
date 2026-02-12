import logging
from typing import List, Type, TypeVar

import requests
from pydantic import BaseModel, ValidationError
from requests.exceptions import HTTPError, RequestException
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import TIMEOUT
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

        status = data.get('status')
        message = data.get('message')
        result_list = data.get('result')

        # Handle Etherscan-like "No transactions found" response
        if status == '0' and message == 'No transactions found':
            return []

        # Handle other API errors that return 200 OK but status '0'
        if status == '0':
            logging.error(f"API error for {endpoint}: {message}. Result: {result_list}")
            return []

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
