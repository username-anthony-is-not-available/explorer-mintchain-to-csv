import os
import threading
from typing import Any, Dict, Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    write_to_textfile,
)


class MetricsCollector:
    """
    Thread-safe collector for API call and batch export performance metrics.

    Maintains both a dedicated Prometheus ``CollectorRegistry`` (suitable for
    one-off CLI runs and textfile export) and in-memory summary counters for
    end-of-run logging.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._init_metrics()

    def _init_metrics(self) -> None:
        self.registry = CollectorRegistry()
        self.api_requests_total = Counter(
            "explorer_api_requests_total",
            "Total outbound HTTP API requests made by the exporter.",
            labelnames=("method", "status_code", "outcome"),
            registry=self.registry,
        )
        self.api_request_duration_seconds = Histogram(
            "explorer_api_request_duration_seconds",
            "Duration of outbound HTTP API requests in seconds.",
            labelnames=("method", "outcome"),
            registry=self.registry,
        )
        self.api_retries_total = Counter(
            "explorer_api_retries_total",
            "Total API request retries triggered after transient errors or rate limits.",
            registry=self.registry,
        )
        self.api_cache_events_total = Counter(
            "explorer_api_cache_events_total",
            "Total API response cache lookups grouped by hit or miss.",
            labelnames=("result",),
            registry=self.registry,
        )
        self.batch_wallets_processed_total = Counter(
            "batch_wallets_processed_total",
            "Total wallet addresses processed in batch runs by outcome.",
            labelnames=("status",),
            registry=self.registry,
        )
        self.transactions_exported_total = Counter(
            "transactions_exported_total",
            "Total transactions exported across chains and output formats.",
            labelnames=("chain", "format"),
            registry=self.registry,
        )
        self.batch_run_duration_seconds = Gauge(
            "batch_run_duration_seconds",
            "Wall-clock duration of the most recent batch run in seconds.",
            registry=self.registry,
        )

        self._api_requests_total = 0
        self._api_requests_success = 0
        self._api_requests_error = 0
        self._api_retries_total = 0
        self._api_cache_hits = 0
        self._api_cache_misses = 0
        self._api_total_duration_seconds = 0.0
        self._wallets_succeeded = 0
        self._wallets_failed = 0
        self._transactions_exported = 0
        self._batch_duration_seconds = 0.0

    def reset(self) -> None:
        """Reset all Prometheus metrics and in-memory summary counters."""
        with self._lock:
            self._init_metrics()

    def record_api_request(
        self,
        method: str,
        duration_seconds: float,
        status_code: Optional[int] = None,
        error_type: str = "",
    ) -> None:
        """Record one outbound HTTP API request attempt and its latency."""
        safe_duration = max(0.0, float(duration_seconds))
        method_label = method.upper()
        status_label = str(status_code) if status_code is not None else "unavailable"

        if error_type:
            outcome = "network_error"
            is_error = True
        elif status_code is not None and status_code >= 400:
            outcome = "http_error"
            is_error = True
        else:
            outcome = "success"
            is_error = False

        with self._lock:
            self.api_requests_total.labels(
                method=method_label,
                status_code=status_label,
                outcome=outcome,
            ).inc()
            self.api_request_duration_seconds.labels(
                method=method_label,
                outcome=outcome,
            ).observe(safe_duration)

            self._api_requests_total += 1
            if is_error:
                self._api_requests_error += 1
            else:
                self._api_requests_success += 1
            self._api_total_duration_seconds += safe_duration

    def record_retry(self) -> None:
        """Record one API request retry attempt."""
        with self._lock:
            self.api_retries_total.inc()
            self._api_retries_total += 1

    def record_cache_hit(self) -> None:
        """Record an API cache hit."""
        with self._lock:
            self.api_cache_events_total.labels(result="hit").inc()
            self._api_cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record an API cache miss."""
        with self._lock:
            self.api_cache_events_total.labels(result="miss").inc()
            self._api_cache_misses += 1

    def record_wallet_processed(self, success: bool) -> None:
        """Record completion status for a single wallet in a batch run."""
        status_label = "success" if success else "error"
        with self._lock:
            self.batch_wallets_processed_total.labels(status=status_label).inc()
            if success:
                self._wallets_succeeded += 1
            else:
                self._wallets_failed += 1

    def record_transactions_exported(
        self, chain: str, output_format: str, count: int
    ) -> None:
        """Record the number of exported transactions for a chain and format."""
        safe_count = max(0, int(count))
        with self._lock:
            if safe_count > 0:
                self.transactions_exported_total.labels(
                    chain=chain,
                    format=output_format,
                ).inc(safe_count)
            self._transactions_exported += safe_count

    def record_batch_duration(self, duration_seconds: float) -> None:
        """Record total wall-clock duration of a batch run in seconds."""
        safe_duration = max(0.0, float(duration_seconds))
        with self._lock:
            self.batch_run_duration_seconds.set(safe_duration)
            self._batch_duration_seconds = safe_duration

    def get_summary(self) -> Dict[str, Any]:
        """Return a thread-safe snapshot of collected performance metrics."""
        with self._lock:
            avg_duration_ms = (
                (self._api_total_duration_seconds / self._api_requests_total) * 1000.0
                if self._api_requests_total > 0
                else 0.0
            )
            return {
                "api_requests_total": self._api_requests_total,
                "api_requests_success": self._api_requests_success,
                "api_requests_error": self._api_requests_error,
                "api_retries_total": self._api_retries_total,
                "api_cache_hits": self._api_cache_hits,
                "api_cache_misses": self._api_cache_misses,
                "api_total_duration_seconds": round(
                    self._api_total_duration_seconds, 6
                ),
                "api_avg_duration_ms": round(avg_duration_ms, 2),
                "wallets_succeeded": self._wallets_succeeded,
                "wallets_failed": self._wallets_failed,
                "transactions_exported": self._transactions_exported,
                "batch_duration_seconds": round(self._batch_duration_seconds, 4),
            }

    def format_summary(self) -> str:
        """Format collected metrics into a concise human-readable log summary."""
        summary = self.get_summary()
        return (
            "Run Metrics Summary: "
            f"wallets_ok={summary['wallets_succeeded']} "
            f"wallets_failed={summary['wallets_failed']} "
            f"transactions_exported={summary['transactions_exported']} "
            f"api_requests={summary['api_requests_total']} "
            f"(ok={summary['api_requests_success']}, err={summary['api_requests_error']}, "
            f"retries={summary['api_retries_total']}) "
            f"cache_hits={summary['api_cache_hits']} "
            f"cache_misses={summary['api_cache_misses']} "
            f"avg_api_ms={summary['api_avg_duration_ms']:.2f} "
            f"batch_duration_s={summary['batch_duration_seconds']:.2f}"
        )

    def render_prometheus(self) -> str:
        """Render collected metrics in Prometheus text exposition format."""
        with self._lock:
            return generate_latest(self.registry).decode("utf-8")

    def write_prometheus_file(self, file_path: str) -> None:
        """Write collected metrics to a Prometheus textfile collector target."""
        parent = os.path.dirname(file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with self._lock:
            write_to_textfile(file_path, self.registry)


metrics_collector = MetricsCollector()
