"""Build coverage upload requests from report files on disk."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from string import hexdigits

from ._generated.models.coverage_upload_request import CoverageUploadRequest
from ._generated.models.uploaded_report import UploadedReport

MAX_REPORTS = 50
MAX_BODY_BYTES = 30 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class CoverageFile:
    """A report file and, optionally, the name the server records for it."""

    path: str | os.PathLike[str]
    name: str | None = None


CoverageFileSpec = str | os.PathLike[str] | CoverageFile


def _tested_sha(value: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(character not in hexdigits for character in value)
    ):
        raise ValueError("tested_sha must be a full 40 character hexadecimal commit SHA.")


def _explicit_name(name: str) -> str:
    parts = PurePosixPath(name.replace("\\", "/")).parts
    if not parts or PurePosixPath(name).is_absolute() or ".." in parts:
        raise ValueError(f"Report name {name!r} must be a relative path without '..'.")
    return "/".join(part for part in parts if part != ".")


def _relative_name(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise ValueError(f"Report {str(path)!r} is outside the root {str(root)!r}.") from None
    return relative.as_posix()


def build_coverage_request(
    tested_sha: str,
    files: Sequence[CoverageFileSpec],
    *,
    root: str | os.PathLike[str] | None = None,
) -> CoverageUploadRequest:
    """Read report files as UTF-8 text and return the upload request for them.

    Each report is named by its path relative to ``root`` (default: the working
    directory) unless a :class:`CoverageFile` gives a name. Nothing is sent: every
    problem is raised as ``ValueError`` before a request exists. Missing files raise
    the usual ``OSError``.
    """
    _tested_sha(tested_sha)
    if isinstance(files, str | os.PathLike) or not 1 <= len(files) <= MAX_REPORTS:
        raise ValueError(f"Upload 1 to {MAX_REPORTS} report files.")
    base = Path(root if root is not None else Path.cwd()).resolve()
    reports: list[UploadedReport] = []
    seen: set[str] = set()
    for spec in files:
        item = spec if isinstance(spec, CoverageFile) else CoverageFile(spec)
        path = Path(item.path)
        resolved = (path if path.is_absolute() else base / path).resolve()
        name = (
            _explicit_name(item.name) if item.name is not None else _relative_name(resolved, base)
        )
        if name in seen:
            raise ValueError(f"Report name {name!r} is used twice.")
        seen.add(name)
        try:
            content = resolved.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"Report {name!r} is not UTF-8 text.") from None
        reports.append(UploadedReport(name=name, content=content))
    request = CoverageUploadRequest(tested_sha=tested_sha, reports=reports)
    if len(json.dumps(request.to_dict()).encode()) > MAX_BODY_BYTES:
        raise ValueError("The coverage upload body would exceed 30 MiB.")
    return request
