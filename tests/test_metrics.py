"""Dedicated test suite for the SDK runtime metrics collector and proxies."""

from __future__ import annotations

import csv
from abc import ABC
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from proofline import (
    AsyncProoflineClient,
    LocalStorageMetricsProxy,
    MetricsCollector,
    MetricsProxy,
    ProoflineClient,
    ProoflineError,
    RequestMetric,
    _transport,
)
from proofline.metrics import CSV_COLUMNS

from .fixtures import FINDING, ORG, TOKEN, finding, page
from .http_server import Reply, Request, Server


class InMemoryMetricsProxy(MetricsProxy):
    def __init__(self) -> None:
        self.metrics: list[RequestMetric] = []

    def push(self, metric: RequestMetric) -> None:
        self.metrics.append(metric)


class FailingMetricsProxy(MetricsProxy):
    def push(self, metric: RequestMetric) -> None:
        raise RuntimeError("backend unavailable")


def test_metrics_proxy_is_abstract() -> None:
    assert issubclass(MetricsProxy, ABC)
    with pytest.raises(TypeError):
        MetricsProxy()  # type: ignore[abstract]


def test_metrics_collector_defaults_to_local_storage_proxy() -> None:
    collector = MetricsCollector()
    assert isinstance(collector.proxy, LocalStorageMetricsProxy)
    assert collector.proxy.directory == Path("metrics")


def test_local_storage_metrics_proxy_appends_csv_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    collector = MetricsCollector()

    first = RequestMetric(
        timestamp="2026-11-14T09:30:00+00:00",
        file_path="/opt/app/service.py",
        class_name="ReviewRunner",
        method_name="fetch_reviews",
        http_method="GET",
        path="/api/v1/organizations/123/reviews",
        status_code=200,
        duration_ms=12.345,
        retries=0,
        error=None,
    )
    second = RequestMetric(
        timestamp="2026-11-14T09:31:00+00:00",
        file_path="/opt/app/cli.py",
        class_name=None,
        method_name="run_cli",
        http_method="POST",
        path="/api/v1/organizations/123/reviews",
        status_code=503,
        duration_ms=45.678,
        retries=3,
        error="Service unavailable",
    )

    collector.record(first)
    collector.record(second)

    report_file = tmp_path / "metrics" / "2026-11-14.csv"
    assert report_file.is_file()

    with report_file.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))

    assert rows[0] == list(CSV_COLUMNS)
    assert len(rows) == 3
    assert rows[1] == [
        "2026-11-14T09:30:00+00:00",
        "/opt/app/service.py",
        "ReviewRunner",
        "fetch_reviews",
        "GET",
        "/api/v1/organizations/123/reviews",
        "200",
        "12.345",
        "0",
        "",
    ]
    assert rows[2] == [
        "2026-11-14T09:31:00+00:00",
        "/opt/app/cli.py",
        "",
        "run_cli",
        "POST",
        "/api/v1/organizations/123/reviews",
        "503",
        "45.678",
        "3",
        "Service unavailable",
    ]


def test_sync_client_emits_metrics_and_writes_csv(tmp_path: Path) -> None:
    proxy = LocalStorageMetricsProxy(directory=tmp_path / "metrics")
    collector = MetricsCollector(proxy=proxy)

    with Server(lambda _req, _n: Reply(body=page())) as peer:
        with ProoflineClient(SecretStr(TOKEN), base_url=peer.url, metrics=collector) as client:
            result = client.list_reviews(ORG)
            assert len(result.items) == 1

    csv_files = list((tmp_path / "metrics").glob("*.csv"))
    assert len(csv_files) == 1
    with csv_files[0].open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    row = rows[0]
    assert Path(row["file_path"]).is_absolute()
    assert row["file_path"].endswith("proofline/client.py")
    assert row["class_name"] == "ProoflineClient"
    assert row["method_name"] == "list_reviews"
    assert row["http_method"] == "GET"
    assert row["path"] == f"/api/v1/organizations/{ORG}/reviews"
    assert row["status_code"] == "200"
    assert float(row["duration_ms"]) >= 0.0
    assert row["retries"] == "0"
    assert row["error"] == ""


async def test_async_client_emits_metrics_with_retries_and_redacted_errors() -> None:
    proxy = InMemoryMetricsProxy()
    collector = MetricsCollector(proxy=proxy)

    def responder(req: Request, count: int) -> Reply:
        if req.path.endswith("/reviews"):
            if count < 2:
                return Reply(
                    status=503,
                    headers={"Retry-After": "0"},
                    body={"type": "unavailable", "detail": "Temporary overload"},
                )
            return Reply(body=page())
        return Reply(
            status=403,
            body={"type": "forbidden", "detail": f"Denied for token {TOKEN}"},
        )

    with Server(responder) as peer:
        async with AsyncProoflineClient(
            SecretStr(TOKEN), base_url=peer.url, metrics=collector
        ) as client:
            reviews = await client.list_reviews(ORG)
            assert len(reviews.items) == 1

            with pytest.raises(ProoflineError) as exc_info:
                await client.get_finding(ORG, FINDING)
            assert exc_info.value.status == 403

    assert len(proxy.metrics) == 2

    first = proxy.metrics[0]
    assert first.class_name == "AsyncProoflineClient"
    assert first.method_name == "list_reviews"
    assert first.http_method == "GET"
    assert first.status_code == 200
    assert first.retries == 2
    assert first.duration_ms >= 0.0
    assert first.error is None

    second = proxy.metrics[1]
    assert second.class_name == "AsyncProoflineClient"
    assert second.method_name == "get_finding"
    assert second.http_method == "GET"
    assert second.status_code == 403
    assert second.retries == 0
    assert second.error == "Denied for token [redacted]"
    assert TOKEN not in (second.error or "")


def test_function_call_without_class_records_none_class_name() -> None:
    proxy = InMemoryMetricsProxy()
    collector = MetricsCollector(proxy=proxy)

    def standalone_caller(url: str) -> int:
        transport = _transport.RetryTransport(SecretStr(TOKEN), 5.0, metrics=collector)
        with httpx.Client(base_url=url, transport=transport) as http_client:
            response = http_client.get(f"/api/v1/organizations/{ORG}/findings/{FINDING}")
            return response.status_code

    with Server(lambda _req, _n: Reply(body=finding())) as peer:
        assert standalone_caller(peer.url) == 200

    assert len(proxy.metrics) == 1
    metric = proxy.metrics[0]
    assert metric.file_path == str(Path(__file__).resolve())
    assert metric.class_name is None
    assert metric.method_name == "standalone_caller"
    assert metric.status_code == 200


async def test_faulty_metrics_proxy_does_not_break_client_requests() -> None:
    collector = MetricsCollector(proxy=FailingMetricsProxy())

    with Server(lambda _req, _n: Reply(body=finding())) as peer:
        with ProoflineClient(SecretStr(TOKEN), base_url=peer.url, metrics=collector) as client:
            sync_result = client.get_finding(ORG, FINDING)
            assert sync_result.id == FINDING

        async with AsyncProoflineClient(
            SecretStr(TOKEN), base_url=peer.url, metrics=collector
        ) as async_client:
            async_result = await async_client.get_finding(ORG, FINDING)
            assert async_result.id == FINDING
