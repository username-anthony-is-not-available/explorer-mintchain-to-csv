import logging
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError

from fetch_blockchain_data import fetch_data, logged_get
from main import main, process_batch_transactions
from metrics import MetricsCollector, metrics_collector
from models import RawTransaction, Transaction


@pytest.fixture(autouse=True)
def reset_global_metrics():
    """Ensure the shared metrics collector starts clean for every test."""
    metrics_collector.reset()
    yield
    metrics_collector.reset()


def test_metrics_collector_records_requests_retries_cache_and_batches(tmp_path):
    collector = MetricsCollector()

    collector.record_api_request("GET", 0.125, status_code=200)
    collector.record_api_request("GET", 0.300, status_code=503)
    collector.record_api_request("GET", 0.075, error_type="ConnectionError")
    collector.record_retry()
    collector.record_cache_hit()
    collector.record_cache_miss()
    collector.record_wallet_processed(success=True)
    collector.record_wallet_processed(success=False)
    collector.record_transactions_exported("mintchain", "csv", 12)
    collector.record_batch_duration(1.2345)

    summary = collector.get_summary()
    assert summary["api_requests_total"] == 3
    assert summary["api_requests_success"] == 1
    assert summary["api_requests_error"] == 2
    assert summary["api_retries_total"] == 1
    assert summary["api_cache_hits"] == 1
    assert summary["api_cache_misses"] == 1
    assert summary["api_total_duration_seconds"] == pytest.approx(0.5, rel=1e-4)
    assert summary["api_avg_duration_ms"] == pytest.approx(166.67, rel=1e-2)
    assert summary["wallets_succeeded"] == 1
    assert summary["wallets_failed"] == 1
    assert summary["transactions_exported"] == 12
    assert summary["batch_duration_seconds"] == pytest.approx(1.2345, rel=1e-4)

    formatted = collector.format_summary()
    assert "wallets_ok=1" in formatted
    assert "wallets_failed=1" in formatted
    assert "transactions_exported=12" in formatted
    assert "api_requests=3" in formatted

    prom_text = collector.render_prometheus()
    assert 'explorer_api_requests_total{method="GET",outcome="success",status_code="200"} 1.0' in prom_text
    assert 'explorer_api_requests_total{method="GET",outcome="http_error",status_code="503"} 1.0' in prom_text
    assert 'explorer_api_requests_total{method="GET",outcome="network_error",status_code="unavailable"} 1.0' in prom_text
    assert "explorer_api_retries_total 1.0" in prom_text
    assert 'explorer_api_cache_events_total{result="hit"} 1.0' in prom_text
    assert 'explorer_api_cache_events_total{result="miss"} 1.0' in prom_text
    assert 'transactions_exported_total{chain="mintchain",format="csv"} 12.0' in prom_text
    assert "batch_run_duration_seconds 1.2345" in prom_text

    prom_file = tmp_path / "metrics" / "run.prom"
    collector.write_prometheus_file(str(prom_file))
    assert prom_file.exists()
    content = prom_file.read_text(encoding="utf-8")
    assert "explorer_api_requests_total" in content


def test_metrics_collector_thread_safety():
    collector = MetricsCollector()

    def worker() -> None:
        for _ in range(50):
            collector.record_api_request("GET", 0.01, status_code=200)
            collector.record_cache_miss()

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(worker) for _ in range(8)]
        for f in futures:
            f.result()

    summary = collector.get_summary()
    assert summary["api_requests_total"] == 400
    assert summary["api_cache_misses"] == 400


def test_logged_get_and_fetch_data_record_metrics(monkeypatch):
    ok_response = Mock(status_code=200)
    ok_response.json.return_value = {"status": "1", "message": "OK", "result": []}

    with patch("fetch_blockchain_data.session.get", return_value=ok_response):
        with patch("fetch_blockchain_data.cache_manager.get_response", return_value=None):
            with patch("fetch_blockchain_data.cache_manager.set_response"):
                result = fetch_data("https://api.example.test/tx", RawTransaction)

    assert result == []
    summary = metrics_collector.get_summary()
    assert summary["api_requests_total"] == 1
    assert summary["api_requests_success"] == 1
    assert summary["api_cache_misses"] == 1
    assert summary["api_cache_hits"] == 0

    cached_payload = {"status": "1", "message": "OK", "result": []}
    with patch("fetch_blockchain_data.cache_manager.get_response", return_value=cached_payload):
        result_cached = fetch_data("https://api.example.test/tx", RawTransaction)

    assert result_cached == []
    summary_after_cache = metrics_collector.get_summary()
    assert summary_after_cache["api_requests_total"] == 1
    assert summary_after_cache["api_cache_hits"] == 1


def test_logged_get_records_network_error_metric():
    with patch(
        "fetch_blockchain_data.session.get",
        side_effect=RequestsConnectionError("network down"),
    ):
        with pytest.raises(RequestsConnectionError):
            logged_get("https://api.example.test/fail")

    summary = metrics_collector.get_summary()
    assert summary["api_requests_total"] == 1
    assert summary["api_requests_error"] == 1
    prom_text = metrics_collector.render_prometheus()
    assert 'outcome="network_error"' in prom_text


@patch("time.sleep", return_value=None)
@patch("fetch_blockchain_data.session.get")
def test_fetch_data_records_retries_metric(mock_get, _mock_sleep):
    mock_get.side_effect = [
        RequestsConnectionError("err1"),
        RequestsConnectionError("err2"),
        Mock(
            status_code=200,
            json=lambda: {"status": "1", "message": "OK", "result": []},
        ),
    ]

    result = fetch_data("https://api.example.test/retry", RawTransaction)
    assert result == []
    summary = metrics_collector.get_summary()
    assert summary["api_retries_total"] == 2
    assert summary["api_requests_total"] == 3
    assert summary["api_requests_error"] == 2
    assert summary["api_requests_success"] == 1


def test_process_batch_transactions_logs_and_records_metrics(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    addr1 = "0x" + "1" * 40
    addr2 = "0x" + "2" * 40

    def fake_process(wallet_address, *args, **kwargs):
        if wallet_address == addr2:
            raise RuntimeError("boom")
        return [
            Transaction.model_validate(
                {
                    "Date": "2023-01-01 00:00:01 UTC",
                    "timestamp": 1,
                    "Description": "tx1",
                    "TxHash": "0x1",
                }
            )
        ]

    with patch("main.process_transactions", side_effect=fake_process):
        with caplog.at_level(logging.INFO):
            process_batch_transactions([addr1, addr2], "mintchain", "csv")

    summary = metrics_collector.get_summary()
    assert summary["wallets_succeeded"] == 1
    assert summary["wallets_failed"] == 1
    assert summary["transactions_exported"] == 1
    assert "Run Metrics Summary:" in caplog.text


def test_main_writes_prometheus_metrics_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "output").mkdir()
    addr = "0x" + "3" * 40
    metrics_path = tmp_path / "prom" / "export.prom"

    with patch(
        "main.process_transactions",
        return_value=[
            Transaction.model_validate(
                {
                    "Date": "2023-01-01 00:00:01 UTC",
                    "timestamp": 1,
                    "Description": "tx1",
                    "TxHash": "0x1",
                }
            )
        ],
    ):
        with patch(
            "sys.argv",
            [
                "main.py",
                "--wallet",
                addr,
                "--format",
                "json",
                "--metrics-file",
                str(metrics_path),
            ],
        ):
            main()

    assert metrics_path.exists()
    content = metrics_path.read_text(encoding="utf-8")
    assert 'batch_wallets_processed_total{status="success"} 1.0' in content
    assert 'transactions_exported_total{chain="mintchain",format="json"} 1.0' in content
