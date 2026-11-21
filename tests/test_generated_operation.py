"""Compatibility of generated SDK models and methods."""

import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from proofline import models

from .http_server import Reply, Server

SDK = Path(__file__).resolve().parents[1]


def test_checkpoint_keeps_its_positional_result() -> None:
    due = datetime(2026, 11, 1, tzinfo=UTC)
    checkpoint = models.DeployCoverageCheckpoint(models.DeployCheckpoint.HOUR_1, due, "REGRESSED")
    assert checkpoint.to_dict()["result"] == "REGRESSED"
    recorded = models.DeployCoverageCheckpoint.from_dict(
        {**checkpoint.to_dict(), "gaps": ["CHANGE_CHECK_MISSING"]}
    )
    assert recorded.result == "REGRESSED"
    assert recorded.gaps == ["CHANGE_CHECK_MISSING"]


def test_new_public_operation(tmp_path: Path) -> None:
    for name in ("proofline", "scripts", "templates"):
        shutil.copytree(SDK / name, tmp_path / name, ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("generator.json", "pyproject.toml"):
        shutil.copyfile(SDK / name, tmp_path / name)
    spec = json.loads((SDK / "openapi.public.json").read_bytes())
    spec["components"]["schemas"]["ExampleResult"] = {
        "type": "object",
        "required": ["answer"],
        "properties": {"answer": {"type": "string"}},
    }
    spec["paths"]["/api/example/{item}"] = {
        "parameters": [
            {"name": "item", "in": "path", "required": True, "schema": {"type": "integer"}}
        ],
        "get": {
            "operationId": "read_example",
            "tags": ["samples"],
            "responses": {
                "200": {
                    "description": "Example",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ExampleResult"}
                        }
                    },
                }
            },
        },
    }
    (tmp_path / "openapi.public.json").write_text(json.dumps(spec))
    subprocess.run([sys.executable, "scripts/generate.py"], cwd=tmp_path, check=True)
    # Import both clients from the newly generated package in a fresh interpreter.
    probe = """
import asyncio, sys
from proofline import ProoflineClient, AsyncProoflineClient, ProoflineError

async def run():
    with ProoflineClient("sample-token", base_url=sys.argv[1]) as client:
        assert client.read_example(7).answer == "seven"
    async with AsyncProoflineClient("sample-token", base_url=sys.argv[1]) as client:
        assert (await client.read_example(7)).answer == "seven"
        try:
            await client.read_example(8)
        except ProoflineError as error:
            assert error.status == 403
        else:
            raise AssertionError("the generated client accepted a forbidden response")
asyncio.run(run())
"""
    with Server(
        lambda r, _: (
            Reply(body={"answer": "seven"})
            if r.path.endswith("/7")
            else Reply(status=403, body={"type": "forbidden", "detail": "Unavailable"})
        )
    ) as peer:
        subprocess.run(
            [sys.executable, "-c", probe, peer.url],
            cwd=tmp_path,
            env={**os.environ, "PYTHONPATH": str(tmp_path)},
            check=True,
        )
        assert [r.path for r in peer.requests] == [
            "/api/example/7",
            "/api/example/7",
            "/api/example/8",
        ]
        assert all(r.headers.get("Authorization") == "Bearer sample-token" for r in peer.requests)
