import responses
import pytest
from requests.exceptions import RequestException
from fetch_blockchain_data import fetch_data
from models import RawTransaction

@responses.activate
def test_fetch_data_rate_limit_in_json():
    mock_url = "https://api.test.com/rate-limit"
    # Mocking a 200 OK response that contains a rate limit message in the JSON
    responses.add(
        responses.GET,
        mock_url,
        json={
            "status": "0",
            "message": "NOTOK",
            "result": "Max rate limit reached"
        },
        status=200
    )

    # We expect fetch_data to return [] after retries because we mocked the failure.
    # Tenacity will retry 5 times by default.
    # To speed up the test, we could mock the retry settings but let's just see if it handles it.
    
    data = fetch_data(mock_url, RawTransaction)
    assert data == []
    
    # Check that it was called multiple times (retries)
    assert len(responses.calls) > 1

@responses.activate
def test_fetch_data_429_retry_after():
    mock_url = "https://api.test.com/429"
    responses.add(
        responses.GET,
        mock_url,
        headers={"Retry-After": "1"},
        status=429
    )
    
    data = fetch_data(mock_url, RawTransaction)
    assert data == []
    assert len(responses.calls) > 1
