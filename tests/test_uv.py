"""The gate can bootstrap its pinned uv on Windows as well as macOS and Linux."""

import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/_uv.py"
spec = importlib.util.spec_from_file_location("_uv", SCRIPT)
assert spec is not None and spec.loader is not None
uv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uv)


@pytest.mark.parametrize(
    ("system", "machine", "target"),
    [
        ("Windows", "AMD64", "x86_64-pc-windows-msvc"),
        ("Windows", "ARM64", "aarch64-pc-windows-msvc"),
        ("Linux", "x86_64", "x86_64-unknown-linux-gnu"),
        ("Darwin", "arm64", "aarch64-apple-darwin"),
    ],
)
def test_supported_platforms_have_a_pinned_archive(system: str, machine: str, target: str) -> None:
    assert uv.release_target(system, machine) == target
    assert target in uv.CHECKSUMS


def test_windows_archive_yields_its_uv_executable() -> None:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("uv.exe", b"uv")
        package.writestr("uvx.exe", b"uvx")
    assert uv.unpack(archive.getvalue(), "x86_64-pc-windows-msvc") == b"uv"


def test_unix_archive_still_yields_its_uv_executable() -> None:
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as package:
        member = tarfile.TarInfo("uv-x86_64-unknown-linux-gnu/uv")
        member.size = 2
        package.addfile(member, io.BytesIO(b"uv"))
    assert uv.unpack(archive.getvalue(), "x86_64-unknown-linux-gnu") == b"uv"
