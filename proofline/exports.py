"""Export requests and bounded export pages with their text and continuation metadata."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal, get_args
from uuid import UUID

import httpx

from ._transport import ProoflineError

ExportDataset = Literal["reviews", "finding_outcomes", "finding_validations", "spend", "findings"]
ExportFormat = Literal["csv", "ndjson"]
ExportTime = str | datetime
_DATASETS: frozenset[str] = frozenset(get_args(ExportDataset))
_MEDIA_TYPES: Mapping[ExportFormat, str] = {"csv": "text/csv", "ndjson": "application/x-ndjson"}


@dataclass(frozen=True)
class ExportPage:
    format: ExportFormat
    text: str
    rows: list[dict[str, Any]]
    version: int
    settled_until: str
    next_cursor: str | None


@dataclass(frozen=True)
class ExportRequest:
    path: str
    params: dict[str, str]
    headers: dict[str, str]


def export_request(
    organization_id: UUID,
    dataset: ExportDataset,
    *,
    from_time: ExportTime,
    to_time: ExportTime,
    format: ExportFormat,
    cursor: str | None,
    group_by: str | None,
) -> ExportRequest:
    if dataset not in _DATASETS:
        raise ValueError("Unknown export dataset.")
    if format not in _MEDIA_TYPES:
        raise ValueError("Export format must be csv or ndjson.")
    if cursor == "":
        raise ValueError("The export cursor must be nonempty.")
    params = {"from": export_time(from_time), "to": export_time(to_time), "format": format}
    if cursor is not None:
        params["cursor"] = cursor
    if group_by is not None:
        params["group_by"] = group_by
    return ExportRequest(
        f"/api/v1/organizations/{organization_id}/exports/{dataset}",
        params,
        {"Accept": _MEDIA_TYPES[format]},
    )


def export_time(value: ExportTime) -> str:
    if isinstance(value, str):
        return value
    if value.utcoffset() is None:
        raise ValueError("Export window datetimes must be timezone-aware.")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def decode_export(response: httpx.Response, format: ExportFormat) -> ExportPage:
    try:
        if (
            response.headers.get("content-type", "").split(";")[0].strip() != _MEDIA_TYPES[format]
            or response.headers.get("x-proofline-export-version") != "1"
        ):
            raise ValueError
        horizon = response.headers["x-proofline-export-settled-until"]
        if datetime.fromisoformat(horizon.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError
        text = response.content.decode("utf-8")
        if format == "csv":
            records = list(csv.reader(io.StringIO(text, newline=""), strict=True))
            columns = records.pop(0)
            if len(set(columns)) != len(columns) or any(
                len(row) != len(columns) for row in records
            ):
                raise ValueError
            rows = [dict(zip(columns, row, strict=True)) for row in records]
        else:
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
        if any(not isinstance(row, dict) or str(row.get("dataset_version")) != "1" for row in rows):
            raise ValueError
        return ExportPage(
            format, text, rows, 1, horizon, response.headers.get("x-proofline-export-next-cursor")
        )
    except (ValueError, KeyError, IndexError, UnicodeError, csv.Error):
        raise ProoflineError(
            response.status_code,
            "urn:proofline:sdk:invalid-response",
            "The export body or metadata is invalid.",
        ) from None
