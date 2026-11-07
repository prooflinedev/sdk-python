"""Verify PyPI release files and select the missing distributions for publication."""

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PACKAGE = "proofline-sdk"
# PyPI's CDN caches the version page for up to 15 minutes (Cache-Control: max-age=900),
# so a page fetched before or during the upload can stay stale that long.
PROPAGATION_SECONDS = 20 * 60
POLL_SECONDS = 30


def published(version: str) -> dict[str, str]:
    try:
        url = f"https://pypi.org/pypi/{PACKAGE}/{version}/json"
        with urllib.request.urlopen(url, timeout=30) as response:
            release = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return {}
        raise
    if release["info"]["name"] != PACKAGE or release["info"]["version"] != version:
        raise ValueError("PyPI returned a different distribution")
    return {file["filename"]: file["digests"]["sha256"] for file in release["urls"]}


def missing(expected: dict[str, str], released: dict[str, str]) -> list[str]:
    for name, digest in released.items():
        if expected.get(name) != digest:
            raise ValueError(f"PyPI has unexpected content for {name}")
    return sorted(expected.keys() - released.keys())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("--pending", type=Path, help="copy only missing files to a new directory")
    args = parser.parse_args()
    if not re.fullmatch(r"(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){2}", args.version):
        raise ValueError("expected a stable package version")
    files = sorted(args.artifacts.iterdir())
    prefix = f"proofline_sdk-{args.version}"
    if {file.name for file in files} != {prefix + ".tar.gz", prefix + "-py3-none-any.whl"}:
        raise ValueError("expected the wheel and source distribution for this version")
    expected = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in files}
    if args.pending:
        names = missing(expected, published(args.version))
        args.pending.mkdir()
        for name in names:
            shutil.copyfile(args.artifacts / name, args.pending / name)
        print(len(names))
        return
    deadline = time.monotonic() + PROPAGATION_SECONDS
    while True:
        try:
            names = missing(expected, published(args.version))
        except OSError as error:
            # A server error, timeout or dropped connection means PyPI does not serve it yet.
            if isinstance(error, urllib.error.HTTPError) and error.code < 500:
                raise
            problem = f"PyPI lookup failed: {error}"
        else:
            if not names:
                return
            problem = "PyPI is missing " + ", ".join(names)
        if time.monotonic() >= deadline:
            sys.exit(problem)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
