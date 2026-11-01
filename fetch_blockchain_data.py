import logging
import time
from typing import Any, Dict, List, Type, TypeVar
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
from pydantic import BaseModel, ValidationError
from requests.exceptions import HTTPError, RequestException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from cache_manager import cache_manager
from config import TIMEOUT
from models import RawTokenTransfer, RawTransaction

# Initialize a global session for connection pooling
session = requests.Session()

T = TypeVar("T", bound=BaseModel)

_SENSITIVE_QUERY_KEYS = {
    "api_key",
    "apikey",
    "auth",
    "authorization",
    "key",
    "password",
    "refresh_token",
    "secret",
    "token",
}


def _is_sensitive_query_key(key: str) -> bool:
    normalized_key = key.lower().replace("-", "_")
    compact_key = normalized_key.replace("_", "")
    return (
        normalized_key in _SENSITIVE_QUERY_KEYS
        or normalized_key.endswith(("_key", "_token", "_secret", "_password"))
        or compact_key.endswith(("key", "token", "secret", "password"))
    )


def _redact_endpoint(endpoint: str) -> str:
    """Return an endpoint safe for logs by redacting credentials and secrets."""
    try:
        parts = urlsplit(endpoint)
        query = urlencode(
            [
                (
                    key,
                    "REDACTED" if _is_sensitive_query_key(key) else value,
                )
                for key, value in parse_qsl(parts.query, keep_blank_values=True)
            ]
        )
        netloc = parts.netloc
        if parts.username is not None or parts.password is not None:
            hostname = parts.hostname or ""
            if ":" in hostname and not hostname.startswith("["):
                hostname = f"[{hostname}]"
            if parts.port:
                hostname = f"{hostname}:{parts.port}"
            netloc = f"REDACTED@{hostname}"
        return urlunsplit(
            (parts.scheme, netloc, parts.path, query, "")
        )
    except ValueError:
        return "<invalid endpoint>"


def _log_request(
    endpoint: str,
    started_at: float,
    status_code: Any = None,
    error_type: str = "",
) -> None:
    """Log one network attempt without exposing credentials in its URL."""
    duration_ms = (time.perf_counter() - started_at) * 1000
    safe_status = status_code if status_code is not None else "unavailable"
    level = logging.WARNING if error_type else logging.INFO
    if isinstance(status_code, int) and status_code >= 400:
        level = logging.WARNING

    message = "API request method=GET url=%s status_code=%s duration_ms=%.2f"
    if error_type:
        message += " error_type=%s"
        logging.log(
            level,
            message,
            _redact_endpoint(endpoint),
            safe_status,
            duration_ms,
            error_type,
        )
    else:
        logging.log(
            level,
            message,
            _redact_endpoint(endpoint),
            safe_status,
            duration_ms,
        )


def logged_get(endpoint: str, **kwargs: Any) -> requests.Response:
    """Perform a shared-session GET and log its status and elapsed time."""
    log_endpoint = endpoint
    params = kwargs.get("params")
    if params:
        try:
            log_endpoint = requests.Request(
                "GET", endpoint, params=params
            ).prepare().url or endpoint
        except Exception:
            # Logging must never prevent the actual request from being attempted.
            pass

    started_at = time.perf_counter()
    try:
        response = session.get(endpoint, **kwargs)
    except Exception as e:
        _log_request(log_endpoint, started_at, error_type=type(e).__name__)
        raise

    _log_request(
        log_endpoint,
        started_at,
        status_code=getattr(response, "status_code", None),
    )
    return response


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
                logging.warning(
                    f"Rate limit exceeded. Retrying after {wait_seconds} seconds."
                )
                return wait_seconds
            except (ValueError, TypeError):
                logging.warning(
                    f"Could not parse 'Retry-After' header: {retry_after}. Falling back to exponential backoff."
                )

    return wait_exponential(multiplier=1, min=4, max=60)(retry_state)


def _log_and_return_empty(retry_state):
    exception = retry_state.outcome.exception()
    logging.error(
        "An error occurred while fetching data after multiple retries: %s",
        type(exception).__name__,
    )
    return []


def _process_response_data(
    data: Dict[str, Any], model: Type[T], endpoint: str
) -> List[T]:
    """
    Processes the JSON response from the explorer API.
    """
    status = data.get("status")
    message = data.get("message")

    # Handle Etherscan-style empty responses gracefully
    if status == "0":
        if message == "No transactions found":
            return []
        if "rate limit" in str(data.get("result", "")).lower() or "rate limit" in str(message).lower():
            logging.warning(
                "API rate limit reached for %s. Triggering retry...",
                _redact_endpoint(endpoint),
            )
            raise RequestException("API rate limit reached")

    # Check for data in 'result' (standard Etherscan) or 'items' (Routescan V2/Blockscout).
    result_list = data.get("result")
    if result_list is None:
        result_list = data.get("items")

    # Handle malformed result formats
    if result_list is None or not isinstance(result_list, list):
        if not (status == "0" and message == "No transactions found"):
            logging.error(
                "API response for %s does not contain a list in 'result' or 'items': %s",
                _redact_endpoint(endpoint),
                data,
            )
        return []

    validated_data: List[T] = []
    for item in result_list:
        try:
            validated_item = model.model_validate(item)
            validated_data.append(validated_item)
        except ValidationError as e:
            logging.warning(
                "Validation error for item in %s: %s. Item: %s",
                _redact_endpoint(endpoint),
                e,
                item,
            )

    return validated_data


@retry(
    stop=stop_after_attempt(5),
    wait=wait_retry_after_or_exponential,
    retry_error_callback=_log_and_return_empty,
    retry=retry_if_exception_type(RequestException),
)
def fetch_data(endpoint: str, model: Type[T]) -> List[T]:
    # Check cache first
    cached_data = cache_manager.get_response(endpoint)
    if cached_data:
        logging.debug("Using cached response for %s", _redact_endpoint(endpoint))
        try:
            return _process_response_data(cached_data, model, endpoint)
        except RequestException:
            # If cached data somehow triggers a rate limit exception (unlikely),
            # treat it as a cache miss or error.
            pass

    try:
        response = logged_get(endpoint, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Only cache successful "OK" responses with actual results
        if data.get("status") == "1":
            cache_manager.set_response(endpoint, data)

        return _process_response_data(data, model, endpoint)

    except Exception as e:
        if isinstance(e, RequestException):
            raise  # Reraise RequestException to be handled by tenacity
        logging.error(
            "An unexpected error occurred while fetching %s: %s",
            _redact_endpoint(endpoint),
            type(e).__name__,
        )
        return []
