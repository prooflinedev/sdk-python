"""Bounded export pages, with their original text and continuation metadata."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

import httpx

from ._transport import ProoflineError

ExportDataset = Literal["reviews", "finding_outcomes", "finding_validations", "spend", "findings"]
ExportFormat = Literal["csv", "ndjson"]


@dataclass(frozen=True)
class ExportPage:
    format: ExportFormat
    text: str
    rows: list[dict[str, Any]]
    version: int
    settled_until: str
    next_cursor: str | None


def decode_export(response: httpx.Response, format: ExportFormat) -> ExportPage:
    try:
        media = "text/csv" if format == "csv" else "application/x-ndjson"
        if (
            response.headers.get("content-type", "").split(";")[0].strip() != media
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
