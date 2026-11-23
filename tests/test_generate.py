"""The committed generated API is reproducible whatever the machine's text encoding."""

import os
import subprocess
import sys
from pathlib import Path

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
