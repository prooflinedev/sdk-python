"""Use uv 0.13.7, verifying the official release archive before execution."""

from __future__ import annotations

import hashlib
import io
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

VERSION = "0.13.7"
# https://github.com/astral-sh/uv/releases/tag/0.13.7
CHECKSUMS = {
    "aarch64-apple-darwin": "81b811b57e4624df7ed3aac148e0359100d9962f3d9dce00aec533dc2e086731",
    "x86_64-apple-darwin": "20c47e4c1f630b8abaff8c291fa9b9aa300fef92c4fbff95adf198b55287cda7",
    "aarch64-unknown-linux-gnu": "71279f8d3c67241e807b9d8db872d1bf541579fb9f08b7d1eb1682196d1e57dc",
    "x86_64-unknown-linux-gnu": "c5221ff41b7892bfc223543883600125f6a47fe845093e0f5bdff4f359196d83",
    "aarch64-pc-windows-msvc": "505d9e65e7692bac3ddf98c66754aa26c5050c409c184af30a881a0a72cc85e3",
    "x86_64-pc-windows-msvc": "0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021",
}


def matching(executable: Path) -> bool:
    try:
        result = subprocess.run(
            [str(executable), "--version"], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.split()[1] == VERSION
    except (OSError, subprocess.SubprocessError, IndexError):
        return False


def release_target(system: str, machine: str) -> str:
    # Windows reports AMD64 or ARM64; macOS reports arm64.
    architecture = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64", "amd64": "x86_64"}
    systems = {"Darwin": "apple-darwin", "Linux": "unknown-linux-gnu", "Windows": "pc-windows-msvc"}
    return f"{architecture.get(machine.lower())}-{systems.get(system)}"


def unpack(content: bytes, target: str) -> bytes:
    """Return the uv executable from a verified release archive."""
    if target.endswith("-windows-msvc"):
        # The Windows release is a zip with uv.exe at its root.
        with zipfile.ZipFile(io.BytesIO(content)) as package:
            return package.read("uv.exe")
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as package:
        member = package.getmember(f"uv-{target}/uv")
        if not member.isfile():
            raise SystemExit("The verified uv archive has no regular uv executable.")
        source = package.extractfile(member)
        if source is None:
            raise SystemExit("The verified uv archive has no uv executable.")
        with source:
            return source.read()


def executable(tools: Path) -> Path:
    installed = shutil.which("uv")
    if installed is not None and matching(Path(installed)):
        return Path(installed)
    target = release_target(platform.system(), platform.machine())
    if target not in CHECKSUMS:
        raise SystemExit("Install uv 0.13.7 to run the gate on this bootstrap platform.")
    windows = target.endswith("-windows-msvc")
    tools.mkdir(parents=True, exist_ok=True)
    suffix = ".zip" if windows else ".tar.gz"
    archive = tools / f"uv-{VERSION}-{target}{suffix}"
    if not archive.exists():
        url = f"https://github.com/astral-sh/uv/releases/download/{VERSION}/uv-{target}{suffix}"
        with urlopen(url, timeout=30) as response:
            content = response.read(64 * 1024 * 1024)
        if hashlib.sha256(content).hexdigest() != CHECKSUMS[target]:
            raise SystemExit("The uv release archive does not match the pinned official checksum.")
        archive.write_bytes(content)
    content = archive.read_bytes()
    if hashlib.sha256(content).hexdigest() != CHECKSUMS[target]:
        raise SystemExit("The cached uv archive does not match the pinned official checksum.")
    binary = tools / f"uv-{VERSION}-{target}{'.exe' if windows else ''}"
    binary.write_bytes(unpack(content, target))
    binary.chmod(0o755)
    if not matching(binary):
        raise SystemExit("The verified uv executable has an unexpected version.")
    return binary
