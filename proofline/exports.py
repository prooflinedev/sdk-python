"""Bounded export pages, with their original text and continuation metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, NoReturn

import httpx2

from ._csv import parse_csv
from ._transport import MAX_RESPONSE_BYTES, ProoflineError

ExportDataset = Literal["reviews", "finding_outcomes", "finding_validations", "spend", "findings"]
ExportFormat = Literal["csv", "ndjson"]

# Version 2 of the finding datasets adds code-lane rows. Version 1 stays accepted from servers
# that have not moved to version 2.
_VERSIONS: dict[str, tuple[str, ...]] = {"findings": ("1", "2"), "finding_validations": ("1", "2")}


@dataclass(frozen=True)
class ExportPage:
    format: ExportFormat
    text: str
    rows: list[dict[str, Any]]
    version: int
    settled_until: str
    next_cursor: str | None


def _reject_json_constant(value: str) -> NoReturn:
    """Reject non-standard JSON numeric constants."""
    raise ValueError(f"Invalid JSON constant: {value}")


def decode_export(
    response: httpx2.Response, format: ExportFormat, dataset: ExportDataset
) -> ExportPage:
    try:
        if len(response.content) > MAX_RESPONSE_BYTES:
            raise ValueError

        media = "text/csv" if format == "csv" else "application/x-ndjson"
        version = response.headers.get("x-proofline-export-version")

        if response.headers.get("content-type", "").split(";")[0].strip().lower() != media or (
            version not in _VERSIONS.get(dataset, ("1",))
        ):
            raise ValueError

        horizon = response.headers["x-proofline-export-settled-until"]

        if datetime.fromisoformat(horizon.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError

        text = response.content.decode("utf-8")

        if format == "csv":
            records = parse_csv(text)
            columns = records.pop(0)

            if len(set(columns)) != len(columns) or any(
                len(row) != len(columns) for row in records
            ):
                raise ValueError

            rows = [dict(zip(columns, row, strict=True)) for row in records]

        else:
            rows = [
                json.loads(line, parse_constant=_reject_json_constant)
                for line in text.split("\n")
                if line.strip()
            ]

        if any(
            not isinstance(row, dict) or str(row.get("dataset_version")) != version for row in rows
        ):
            raise ValueError

        return ExportPage(
            format,
            text,
            rows,
            int(version),
            horizon,
            response.headers.get("x-proofline-export-next-cursor"),
        )

    except (ValueError, KeyError, IndexError, UnicodeError):
        raise ProoflineError(
            response.status_code,
            "urn:proofline:sdk:invalid-response",
            "The export body or metadata is invalid.",
        ) from None
