"""The gate can bootstrap its pinned uv on Windows as well as macOS and Linux."""

import hashlib
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


def windows_zip() -> bytes:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("uv.exe", b"uv")
    return archive.getvalue()


def fake_windows(
    monkeypatch: pytest.MonkeyPatch, machine: str, content: bytes
) -> tuple[list[str], list[Path]]:
    """Pretend to be Windows with no matching uv installed; serve `content` as the release.

    Returns the requested URLs and the executables whose version was checked.
    """
    requested: list[str] = []
    checked: list[Path] = []

    def download(url: str, timeout: int) -> io.BytesIO:
        requested.append(url)
        return io.BytesIO(content)

    monkeypatch.setattr(uv.shutil, "which", lambda name: None)
    monkeypatch.setattr(uv.platform, "system", lambda: "Windows")
    monkeypatch.setattr(uv.platform, "machine", lambda: machine)
    monkeypatch.setattr(uv, "urlopen", download)

    def matching(executable: Path) -> bool:
        checked.append(executable)
        return True

    monkeypatch.setattr(uv, "matching", matching)
    return requested, checked


@pytest.mark.parametrize(
    ("machine", "target"),
    [("AMD64", "x86_64-pc-windows-msvc"), ("ARM64", "aarch64-pc-windows-msvc")],
)
def test_windows_bootstrap_downloads_the_zip_and_saves_an_exe(
    machine: str, target: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = windows_zip()
    requested, checked = fake_windows(monkeypatch, machine, content)
    monkeypatch.setitem(uv.CHECKSUMS, target, hashlib.sha256(content).hexdigest())
    binary = uv.executable(tmp_path)
    assert requested == [
        f"https://github.com/astral-sh/uv/releases/download/{uv.VERSION}/uv-{target}.zip"
    ]
    assert binary == tmp_path / f"uv-{uv.VERSION}-{target}.exe"
    assert binary.read_bytes() == b"uv"
    assert checked == [binary]


@pytest.mark.parametrize(
    ("cached", "message"),
    [(False, "release archive does not match"), (True, "cached uv archive does not match")],
)
def test_windows_zip_with_a_wrong_checksum_is_refused(
    cached: bool, message: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = windows_zip()
    fake_windows(monkeypatch, "AMD64", content)
    target = "x86_64-pc-windows-msvc"
    monkeypatch.setitem(uv.CHECKSUMS, target, "0" * 64)

    def unpack(content: bytes, target: str) -> bytes:
        raise AssertionError("an unverified archive was unpacked")

    monkeypatch.setattr(uv, "unpack", unpack)
    archive = tmp_path / f"uv-{uv.VERSION}-{target}.zip"
    if cached:
        archive.write_bytes(content)
    with pytest.raises(SystemExit, match=message):
        uv.executable(tmp_path)
    # A rejected download is never saved, and a rejected archive is never extracted.
    assert archive.exists() == cached
    assert not (tmp_path / f"uv-{uv.VERSION}-{target}.exe").exists()


def test_unix_archive_still_yields_its_uv_executable() -> None:
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as package:
        member = tarfile.TarInfo("uv-x86_64-unknown-linux-gnu/uv")
        member.size = 2
        package.addfile(member, io.BytesIO(b"uv"))
    assert uv.unpack(archive.getvalue(), "x86_64-unknown-linux-gnu") == b"uv"
