# PRD001: Metrics Collector

**BRD:** [BRD001: SDK Runtime Metrics](../brd/BRD001-runtime-metrics.md)

## Overview
Add a metrics collector and proxy architecture to `ProoflineClient` and `AsyncProoflineClient`. `MetricsCollector` captures runtime and caller metadata for each SDK operation and pushes events to a `MetricsProxy` backend. By default, `MetricsCollector` uses `LocalStorageMetricsProxy`, which appends records to a daily CSV report (`metrics/{date}.csv`).

## Specification

### 1. Data Model & Proxy Abstraction (`proofline/metrics.py`)
- **`RequestMetric` (frozen dataclass):**
  - `timestamp: str` (ISO-8601 UTC)
  - `file_path: str` (full path to the source file)
  - `class_name: str | None` (enclosing class name if applicable, else `None`/empty)
  - `method_name: str` (function or method name)
  - `http_method: str`
  - `path: str`
  - `status_code: int | None`
  - `duration_ms: float`
  - `retries: int`
  - `error: str | None`
- **`MetricsProxy` (abstract base class `ABC`):**
  - Responsible for forwarding metrics to a concrete backend (e.g., Prometheus, OpenTelemetry, local storage).
  - Defines `@abstractmethod def push(self, metric: RequestMetric) -> None`.
- **`LocalStorageMetricsProxy(MetricsProxy)`:**
  - Only concrete proxy implemented in this PRD; used as the **default** proxy.
  - Writes to `metrics/{date}.csv` (with `{date}` formatted as `YYYY-MM-DD`) in append-only mode (`"a"`).
  - Automatically creates the `metrics/` directory and writes the CSV header row when creating a new file.
  - CSV columns: `timestamp,file_path,class_name,method_name,http_method,path,status_code,duration_ms,retries,error`.
- **`MetricsCollector`:**
  - Initialized with `proxy: MetricsProxy | None = None`, defaulting to `LocalStorageMetricsProxy()`.
  - `record(self, metric: RequestMetric) -> None` pushes the collected metric to `self.proxy.push(metric)`.

### 2. Transport & Client Integration (`proofline/_transport.py`, `proofline/client.py`)
- Accept `metrics: MetricsCollector | None = None` in `ProoflineClient.__init__` and `AsyncProoflineClient.__init__` (or default `MetricsCollector(LocalStorageMetricsProxy())` when enabled).
- Capture caller/execution context (`file_path` as full resolved path, `class_name` if called on a class instance, `method_name`) and measure request wall-clock time via `time.perf_counter()`.
- Emit `RequestMetric` via `metrics.record(...)` once per completed operation (including retries), which delegates to `proxy.push(...)`.
- Never let exceptions raised inside `metrics.record` or `proxy.push` break SDK calls (ignore or log safely).
- Redact API token from `error` if present.

### 3. Public Exports (`proofline/__init__.py`)
- Export `RequestMetric`, `MetricsProxy`, `LocalStorageMetricsProxy`, and `MetricsCollector` in `__all__`.

## Target Files
- `proofline/metrics.py` (new)
- `proofline/_transport.py`
- `proofline/client.py`
- `proofline/__init__.py`
- `tests/test_metrics.py` (new)

## Acceptance Criteria
- [ ] `MetricsProxy` is defined as an `ABC` and `MetricsCollector` pushes metrics to its configured proxy.
- [ ] `MetricsCollector()` defaults to `LocalStorageMetricsProxy`.
- [ ] `LocalStorageMetricsProxy` appends metrics to `metrics/{date}.csv` with header and full file path, class (if applicable), method, and request metrics data.
- [ ] Sync and async clients emit `RequestMetric` with accurate status, retry count, and `duration_ms >= 0`.
- [ ] Faulty `MetricsProxy.push` raising an exception does not fail the client request.
- [ ] `pytest` and `mypy` pass with 100% type coverage on new code.
