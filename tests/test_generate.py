"""The committed generated API is reproducible whatever the machine's text encoding."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]


def test_generation_does_not_depend_on_the_locale_encoding() -> None:
    # Windows defaults to a legacy code page such as cp1252, and a C locale to ASCII.
    # -X utf8=0 keeps Python from switching to UTF-8 on its own.
    env = {name: value for name, value in os.environ.items() if name != "PYTHONUTF8"}
    env.update({"LC_ALL": "C", "LANG": "C", "PYTHONCOERCECLOCALE": "0"})
    result = subprocess.run(
        [sys.executable, "-X", "utf8=0", "scripts/generate.py", "--check"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, result.stderr


def load_generate() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate", ROOT / "scripts/generate.py")
    assert spec is not None and spec.loader is not None
    generate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generate)
    return generate


def test_check_treats_a_crlf_working_copy_as_unchanged() -> None:
    generate = load_generate()
    assert generate.text(b"a = 1\r\nb = 2\r\n") == b"a = 1\nb = 2\n"
    assert generate.text(b"\0binary\r\n") == b"\0binary\r\n"


def test_generated_files_use_lf_line_endings(tmp_path: Path) -> None:
    # Windows text writes produce CRLF; the check compares with line endings
    # normalized, so assert the generator's own output directly.
    generate = load_generate()
    destination = tmp_path / "generated"
    generate.generate(destination)
    files = [path for path in destination.rglob("*") if path.is_file()]
    assert files
    assert [path for path in files if b"\r\n" in path.read_bytes()] == []
