"""Use uv 0.10.12, verifying the official release archive before execution."""

from __future__ import annotations

import hashlib
import io
import platform
import shutil
import subprocess
import tarfile
from pathlib import Path
from urllib.request import urlopen

VERSION = "0.10.12"
# https://github.com/astral-sh/uv/releases/tag/0.10.12
CHECKSUMS = {
    "aarch64-apple-darwin": "ae738b5661a900579ec621d3918c0ef17bdec0da2a8a6d8b161137cd15f25414",
    "x86_64-apple-darwin": "17443e293f2ae407bb2d8d34b875ebfe0ae01cf1296de5647e69e7b2e2b428f0",
    "aarch64-unknown-linux-gnu": "0ed7d20f49f6b9b60d45fdfcac28f3ac01a671a6ef08672401ed2833423fea2a",
    "x86_64-unknown-linux-gnu": "ec72570c9d1f33021aa80b176d7baba390de2cfeb1abcbefca346d563bf17484",
}


def matching(executable: Path) -> bool:
    try:
        result = subprocess.run(
            [str(executable), "--version"], capture_output=True, text=True, check=True, timeout=10
        )
        return result.stdout.split()[1] == VERSION
    except (OSError, subprocess.SubprocessError, IndexError):
        return False


def executable(tools: Path) -> Path:
    installed = shutil.which("uv")
    if installed is not None and matching(Path(installed)):
        return Path(installed)
    architecture = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}.get(
        platform.machine()
    )
    system = {"Darwin": "apple-darwin", "Linux": "unknown-linux-gnu"}.get(platform.system())
    target = f"{architecture}-{system}"
    if target not in CHECKSUMS:
        raise SystemExit("Install uv 0.10.12 to run the gate on this bootstrap platform.")
    tools.mkdir(parents=True, exist_ok=True)
    archive = tools / f"uv-{VERSION}-{target}.tar.gz"
    if not archive.exists():
        url = f"https://github.com/astral-sh/uv/releases/download/{VERSION}/uv-{target}.tar.gz"
        with urlopen(url, timeout=30) as response:
            content = response.read(64 * 1024 * 1024)
        if hashlib.sha256(content).hexdigest() != CHECKSUMS[target]:
            raise SystemExit("The uv release archive does not match the pinned official checksum.")
        archive.write_bytes(content)
    content = archive.read_bytes()
    if hashlib.sha256(content).hexdigest() != CHECKSUMS[target]:
        raise SystemExit("The cached uv archive does not match the pinned official checksum.")
    binary = tools / f"uv-{VERSION}-{target}"
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as package:
        member = package.getmember(f"uv-{target}/uv")
        if not member.isfile():
            raise SystemExit("The verified uv archive has no regular uv executable.")
        source = package.extractfile(member)
        if source is None:
            raise SystemExit("The verified uv archive has no uv executable.")
        with source:
            binary.write_bytes(source.read())
    binary.chmod(0o755)
    if not matching(binary):
        raise SystemExit("The verified uv executable has an unexpected version.")
    return binary
