"""Bounded export pages, with their original text and continuation metadata."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TextIO

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


class ExportWriter:
    """Write consecutive export pages to a caller owned text stream.

    CSV headers are emitted once. Format and CSV schema changes are refused
    before the offending page is written. The stream remains open.
    """

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream
        self._format: ExportFormat | None = None
        self._columns: list[str] | None = None

    def write_page(self, page: ExportPage) -> None:
        """Append a page, omitting repeated headers and adding a final newline if needed."""
        if page.format not in ("csv", "ndjson"):
            raise ValueError("Export format must be csv or ndjson.")
        if self._format is not None and page.format != self._format:
            raise ValueError("Export pages must use the same format.")
        text = page.text
        columns = None
        if page.format == "csv":
            source = io.StringIO(text, newline="")
            try:
                columns = next(csv.reader(source, strict=True))
            except (StopIteration, csv.Error):
                raise ValueError("CSV export page must contain a valid header.") from None
            if not columns or len(set(columns)) != len(columns):
                raise ValueError("CSV export page must contain unique column names.")
            if self._columns is not None:
                if columns != self._columns:
                    raise ValueError("CSV export pages must use the same columns in order.")
                text = source.read()
        if text and not text.endswith("\n" if page.format == "ndjson" else ("\n", "\r")):
            # A final record may have no newline. Separate the next page.
            text += "\n"
        self._stream.write(text)
        self._format = page.format
        self._columns = columns


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
