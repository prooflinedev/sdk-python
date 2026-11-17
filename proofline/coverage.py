"""Build coverage upload requests from report files on disk."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from pathlib import Path

from ._generated.models.coverage_upload_request import CoverageUploadRequest
from ._generated.models.uploaded_report import UploadedReport

PathInput = str | os.PathLike[str]

MAX_REPORTS = 50
_FULL_SHA = re.compile(r"[0-9a-f]{40}")


def tested_sha_value(tested_sha: str | None) -> str:
    """Return the full commit SHA, falling back to ``GITHUB_SHA`` from CI."""
    value = tested_sha if tested_sha is not None else os.environ.get("GITHUB_SHA")
    if value is None:
        raise ValueError(
            "Pass tested_sha or set GITHUB_SHA to the full 40-character commit the tests ran on."
        )
    value = value.strip()
    if not _FULL_SHA.fullmatch(value):
        raise ValueError("The tested commit must be a full 40-character lowercase hex SHA.")
    return value


def coverage_request(
    paths: Iterable[PathInput],
    *,
    tested_sha: str | None = None,
    root: PathInput | None = None,
) -> CoverageUploadRequest:
    """Read report files into a coverage upload request.

    Each report is named by its path relative to ``root`` (the current directory by
    default), written with forward slashes, so ``web/lcov.info`` is the same name on
    every platform. Reports must sit inside ``root`` and must have distinct names.
    """
    if isinstance(paths, (str, os.PathLike)):
        raise TypeError("paths must be a sequence of report paths, not a single path.")
    sha = tested_sha_value(tested_sha)
    base = Path(root if root is not None else Path.cwd()).resolve()
    files = [Path(path) for path in paths]
    if not 1 <= len(files) <= MAX_REPORTS:
        raise ValueError(f"Upload 1 to {MAX_REPORTS} coverage reports per request.")
    reports: list[UploadedReport] = []
    seen: set[str] = set()
    for file in files:
        resolved = (base / file).resolve()
        try:
            name = resolved.relative_to(base).as_posix()
        except ValueError:
            raise ValueError(f"{file} is outside the report root {base}.") from None
        if name in seen:
            raise ValueError(f"The coverage report name {name} appears more than once.")
        seen.add(name)
        reports.append(UploadedReport(name=name, content=resolved.read_text(encoding="utf-8")))
    return CoverageUploadRequest(tested_sha=sha, reports=reports)
