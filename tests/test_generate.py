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


def test_check_treats_a_crlf_working_copy_as_unchanged(tmp_path: Path) -> None:
    generate = load_generate()
    for name, newline in (("lf", b"\n"), ("crlf", b"\r\n")):
        (tmp_path / name / "models").mkdir(parents=True)
        (tmp_path / name / "models" / "a.py").write_bytes(b"a = 1" + newline + b"b = 2" + newline)
    assert generate.files(tmp_path / "lf") == generate.files(tmp_path / "crlf")
    # A file with a NUL byte is binary and still compared byte for byte.
    (tmp_path / "lf" / "data.bin").write_bytes(b"\0\n")
    (tmp_path / "crlf" / "data.bin").write_bytes(b"\0\r\n")
    assert generate.files(tmp_path / "lf") != generate.files(tmp_path / "crlf")


def test_generated_python_is_formatted_with_lf_line_endings(tmp_path: Path) -> None:
    # Windows text writes produce CRLF; the formatting step must turn them into LF.
    (tmp_path / "model.py").write_bytes(b"a = 1\r\nb = 2\r\n")
    load_generate().format_python(tmp_path)
    assert (tmp_path / "model.py").read_bytes() == b"a = 1\nb = 2\n"
