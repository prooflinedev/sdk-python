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


def published(version):
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{PACKAGE}/{version}/json", timeout=30) as response:
            release = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return {}
        raise
    if release["info"]["name"] != PACKAGE or release["info"]["version"] != version:
        raise ValueError("PyPI returned a different distribution")
    return {file["filename"]: file["digests"]["sha256"] for file in release["urls"]}


def missing(expected, released):
    for name, digest in released.items():
        if expected.get(name) != digest:
            raise ValueError(f"PyPI has unexpected content for {name}")
    return sorted(expected.keys() - released.keys())


def main():
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
    for attempt in range(6):
        names = missing(expected, published(args.version))
        if not names:
            return
        if attempt < 5:
            time.sleep(5)
    sys.exit("PyPI is missing " + ", ".join(names))


if __name__ == "__main__":
    main()
