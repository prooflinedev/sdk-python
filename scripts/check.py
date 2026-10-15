"""Bootstrap pinned tools, verify generated code and test both packaged artifacts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from _uv import executable

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements-dev.txt"


def python_at(directory: Path) -> Path:
    return directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def command(*args: str, cwd: Path = ROOT) -> None:
    env = dict(os.environ)
    for name in ("PYTHONPATH", "PYTHONHOME", "PROOFLINE_TOKEN"):
        env.pop(name, None)
    for name in tuple(env):
        if name.startswith("UV_"):
            env.pop(name)
    env["PYTHONNOUSERSITE"] = "1"
    env["UV_CACHE_DIR"] = str(ROOT / ".tools/cache")
    env["UV_PYTHON_INSTALL_DIR"] = str(ROOT / ".tools/python")
    env["UV_NO_PROGRESS"] = "1"
    subprocess.run(list(args), check=True, cwd=cwd, env=env)


def run(python: Path, *args: str, cwd: Path = ROOT) -> None:
    command(str(python), *args, cwd=cwd)


def dependencies(uv: Path, python: Path) -> None:
    command(
        str(uv),
        "--no-config",
        "pip",
        "install",
        "--python",
        str(python),
        "--require-hashes",
        "--only-binary=:all:",
        "--index-url",
        "https://pypi.org/simple",
        "-r",
        str(LOCK),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--artifacts", type=Path)
    args = parser.parse_args()
    if args.prepare and args.artifacts is not None:
        parser.error("--prepare and --artifacts are mutually exclusive")
    artifacts_path = args.artifacts.resolve() if args.artifacts is not None else None
    if artifacts_path is not None:
        if artifacts_path.exists() or args.artifacts.is_symlink():
            parser.error("--artifacts requires a fresh, nonexisting directory")
        artifacts_path.mkdir(parents=True)
    uv = executable(ROOT / ".tools")
    runtime = sys.executable if sys.version_info >= (3, 11) else "3.13.12"
    if args.prepare:
        prepared = ROOT / ".venv"
        command(str(uv), "--no-config", "venv", "--clear", "--python", runtime, str(prepared))
        python = python_at(prepared)
        dependencies(uv, python)
        command(
            str(uv),
            "--no-config",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            "--no-build-isolation",
            str(ROOT),
        )
        print("Python SDK wheel prepared in python/.venv for real-server integration.")
        return
    with tempfile.TemporaryDirectory(prefix="proofline-sdk-check-") as temporary:
        workspace = Path(temporary)
        tools = workspace / "tools"
        command(str(uv), "--no-config", "venv", "--python", runtime, str(tools))
        python = python_at(tools)
        dependencies(uv, python)
        run(python, "scripts/generate.py", "--check")
        run(python, "scripts/contracts.py")
        run(python, "-m", "ruff", "check", ".")
        run(python, "-m", "ruff", "format", "--check", ".")
        run(python, "-m", "mypy", "proofline", "scripts")
        run(python, "-m", "pytest", "-q")
        dist = artifacts_path if artifacts_path is not None else workspace / "dist"
        run(python, "-m", "build", "--no-isolation", "--outdir", str(dist))
        artifacts = sorted(dist.iterdir())
        if len(artifacts) != 2 or {path.suffix for path in artifacts} != {".whl", ".gz"}:
            raise SystemExit("The build must produce one wheel and one source distribution.")
        for index, artifact in enumerate(artifacts):
            installed = workspace / f"installed-{index}"
            command(str(uv), "--no-config", "venv", "--python", runtime, str(installed))
            installed_python = python_at(installed)
            dependencies(uv, installed_python)
            command(
                str(uv),
                "--no-config",
                "pip",
                "install",
                "--python",
                str(installed_python),
                "--no-deps",
                "--no-build-isolation",
                str(artifact),
                cwd=workspace,
            )
            run(installed_python, "-I", str(ROOT / "scripts/install_smoke.py"), cwd=workspace)
    print("Python SDK generation, HTTP contracts, wheel and source installs passed.")


if __name__ == "__main__":
    main()
