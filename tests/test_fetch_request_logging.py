import logging

from fetch_blockchain_data import _log_request, _redact_endpoint


def test_redact_endpoint_hides_user_info_and_secret_query_values():
    endpoint = (
        "https://alice:password@example.test:8443/api"
        "?x-api-key=secret-key&client_secret=secret-value"
        "&accessToken=camel-token&clientSecret=camel-secret&wallet=0x123"
        "#access_token=fragment-secret"
    )

    safe_endpoint = _redact_endpoint(endpoint)

    assert safe_endpoint == (
        "https://REDACTED@example.test:8443/api"
        "?x-api-key=REDACTED&client_secret=REDACTED"
        "&accessToken=REDACTED&clientSecret=REDACTED&wallet=0x123"
    )
    assert "alice" not in safe_endpoint
    assert "password" not in safe_endpoint
    assert "secret-key" not in safe_endpoint
    assert "secret-value" not in safe_endpoint
    assert "camel-token" not in safe_endpoint
    assert "camel-secret" not in safe_endpoint
    assert "fragment-secret" not in safe_endpoint


def test_redact_endpoint_hides_malformed_urls():
    assert _redact_endpoint("https://[") == "<invalid endpoint>"


def test_log_request_warns_for_http_error_status(caplog, monkeypatch):
    monkeypatch.setattr("fetch_blockchain_data.time.perf_counter", lambda: 5.25)

    with caplog.at_level(logging.WARNING):
        _log_request(
            "https://api.example.test/tx?api_key=do-not-log",
            started_at=5.0,
            status_code=503,
        )

    assert "status_code=503" in caplog.text
    assert "duration_ms=250.00" in caplog.text
    assert "api_key=REDACTED" in caplog.text
    assert "do-not-log" not in caplog.text
    assert any(record.levelno == logging.WARNING for record in caplog.records)
