# PRD001: Metrics Collector

**BRD:** [BRD001: SDK Runtime Metrics](../brd/BRD001-runtime-metrics.md)

## Overview
Add an optional metrics collector interface to `ProoflineClient` and `AsyncProoflineClient` that receives a telemetry event after each HTTP request completes or fails.

## Specification

### 1. Data Model (`proofline/metrics.py`)
Define an immutable event and collector protocol:
- `RequestMetric(method: str, path: str, status_code: int | None, duration_ms: float, retries: int, error: str | None)` (frozen dataclass)
- `MetricsCollector`: `Protocol` with `record(self, metric: RequestMetric) -> None`

### 2. Transport Integration (`proofline/_transport.py`, `proofline/client.py`)
- Accept `metrics: MetricsCollector | None = None` in `ProoflineClient.__init__` and `AsyncProoflineClient.__init__`.
- Measure request wall-clock time using `time.perf_counter()`.
- Emit `RequestMetric` via `metrics.record(...)` once per completed operation (including retries).
- Never let exceptions raised inside `metrics.record` break SDK calls (ignore or log safely).
- Redact API token from `error` if present.

### 3. Public Exports (`proofline/__init__.py`)
- Export `RequestMetric` and `MetricsCollector` in `__all__`.

## Target Files
- `proofline/metrics.py` (new)
- `proofline/_transport.py`
- `proofline/client.py`
- `proofline/__init__.py`
- `tests/test_metrics.py` (new)

## Acceptance Criteria
- [ ] Sync and async clients emit `RequestMetric` with accurate status, retry count, and `duration_ms >= 0`.
- [ ] Faulty `MetricsCollector.record` raising an exception does not fail the client request.
- [ ] `pytest` and `mypy` pass with 100% type coverage on new code.
