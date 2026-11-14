"""Runtime metrics collector and backend proxy abstractions."""

from __future__ import annotations

import csv
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import FrameType

CSV_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "file_path",
    "class_name",
    "method_name",
    "http_method",
    "path",
    "status_code",
    "duration_ms",
    "retries",
    "error",
)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_INTERNAL_FILES = {
    str((_PACKAGE_ROOT / "metrics.py").resolve()),
    str((_PACKAGE_ROOT / "_transport.py").resolve()),
    str((_PACKAGE_ROOT / "_sync_http.py").resolve()),
}
_GENERATED_API_DIR = str((_PACKAGE_ROOT / "_generated" / "api" / "default").resolve())


@dataclass(frozen=True)
class RequestMetric:
    """Telemetry record emitted for a completed or failed SDK HTTP operation."""

    timestamp: str
    file_path: str
    class_name: str | None
    method_name: str
    http_method: str
    path: str
    status_code: int | None
    duration_ms: float
    retries: int
    error: str | None = None


class MetricsProxy(ABC):
    """Abstract backend interface responsible for storing or exporting metrics."""

    @abstractmethod
    def push(self, metric: RequestMetric) -> None:
        """Forward a single request metric to the underlying backend."""


def _extract_date(timestamp: str) -> str:
    if (
        len(timestamp) >= 10
        and timestamp[4] == "-"
        and timestamp[7] == "-"
        and timestamp[:4].isdigit()
        and timestamp[5:7].isdigit()
        and timestamp[8:10].isdigit()
    ):
        return timestamp[:10]
    return datetime.now(UTC).strftime("%Y-%m-%d")


class LocalStorageMetricsProxy(MetricsProxy):
    """Default metrics proxy that appends records to ``metrics/{date}.csv``."""

    def __init__(self, directory: str | Path = "metrics") -> None:
        self._directory = Path(directory)

    @property
    def directory(self) -> Path:
        return self._directory

    def report_path(self, date_str: str | None = None) -> Path:
        day = date_str or datetime.now(UTC).strftime("%Y-%m-%d")
        return self._directory / f"{day}.csv"

    def push(self, metric: RequestMetric) -> None:
        day = _extract_date(metric.timestamp)
        target = self.report_path(day)
        target.parent.mkdir(parents=True, exist_ok=True)
        write_header = not target.exists() or target.stat().st_size == 0
        with target.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            if write_header:
                writer.writerow(CSV_COLUMNS)
            writer.writerow(
                [
                    metric.timestamp,
                    metric.file_path,
                    metric.class_name or "",
                    metric.method_name,
                    metric.http_method,
                    metric.path,
                    "" if metric.status_code is None else str(metric.status_code),
                    f"{metric.duration_ms:.3f}",
                    str(metric.retries),
                    metric.error or "",
                ]
            )


class MetricsCollector:
    """Collects SDK runtime metrics and pushes them to a configured MetricsProxy."""

    def __init__(self, proxy: MetricsProxy | None = None) -> None:
        self._proxy: MetricsProxy = proxy if proxy is not None else LocalStorageMetricsProxy()

    @property
    def proxy(self) -> MetricsProxy:
        return self._proxy

    def record(self, metric: RequestMetric) -> None:
        try:
            self._proxy.push(metric)
        except Exception:
            pass


def _frame_class_name(frame: FrameType) -> str | None:
    instance = frame.f_locals.get("self")
    if instance is not None:
        return type(instance).__name__
    cls_obj = frame.f_locals.get("cls")
    if isinstance(cls_obj, type):
        return cls_obj.__name__
    qualname = getattr(frame.f_code, "co_qualname", "")
    if "." in qualname:
        prefix = qualname.rsplit(".", 1)[0]
        if "<locals>" not in prefix:
            return prefix.split(".")[-1]
    return None


def _is_skip_frame(frame: FrameType) -> bool:
    filename = str(Path(frame.f_code.co_filename).resolve())
    if filename in _INTERNAL_FILES:
        return True
    module_name = frame.f_globals.get("__name__", "")
    if isinstance(module_name, str) and module_name.startswith(
        ("httpx", "httpcore", "anyio", "asyncio", "contextlib")
    ):
        return True
    if frame.f_code.co_name == "_call" and filename == str((_PACKAGE_ROOT / "client.py").resolve()):
        return True
    if filename.startswith(_GENERATED_API_DIR):
        caller = frame.f_back
        if caller is not None:
            caller_file = str(Path(caller.f_code.co_filename).resolve())
            if caller_file.startswith(str(_PACKAGE_ROOT)):
                return True
    return False


def resolve_call_context() -> tuple[str, str | None, str]:
    """Return ``(file_path, class_name, method_name)`` for the active SDK operation."""
    frame = inspect.currentframe()
    try:
        cursor = frame.f_back if frame is not None else None
        fallback: FrameType | None = None
        while cursor is not None:
            fallback = cursor
            if not _is_skip_frame(cursor):
                return (
                    str(Path(cursor.f_code.co_filename).resolve()),
                    _frame_class_name(cursor),
                    cursor.f_code.co_name,
                )
            cursor = cursor.f_back
        if fallback is not None:
            return (
                str(Path(fallback.f_code.co_filename).resolve()),
                _frame_class_name(fallback),
                fallback.f_code.co_name,
            )
        return ("", None, "")
    finally:
        del frame
