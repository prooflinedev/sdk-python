from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr

from proofline import AsyncProoflineClient, CoverageUploadResponse, ProoflineClient
from proofline.coverage import MAX_REPORTS, coverage_request

from .fixtures import ORG, REPOSITORY, REVIEW, TOKEN
from .http_server import Reply, Request, Server

SHA = "a" * 40
LCOV = "SF:src/main.py\nDA:1,1\nDA:2,0\nend_of_record\n"
MODES = pytest.mark.parametrize("mode", ["sync", "async"])


@pytest.fixture(autouse=True)
def no_ci_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_SHA", raising=False)


@asynccontextmanager
async def session(mode: str, url: str) -> AsyncIterator[Any]:
    if mode == "sync":
        with ProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            yield client
    else:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            yield client


def write(root: Path, name: str, content: str = LCOV) -> Path:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_names_are_relative_to_root_with_forward_slashes(tmp_path: Path) -> None:
    web = write(tmp_path, "web/lcov.info", "web report")
    write(tmp_path, "python/lcov.info", "python report")

    request = coverage_request([web, Path("python/lcov.info")], tested_sha=SHA, root=tmp_path)

    assert request.tested_sha == SHA
    assert [(r.name, r.content) for r in request.reports] == [
        ("web/lcov.info", "web report"),
        ("python/lcov.info", "python report"),
    ]


def test_root_defaults_to_the_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path, "lcov.info")
    monkeypatch.chdir(tmp_path)

    request = coverage_request(["lcov.info"], tested_sha=SHA)

    assert [r.name for r in request.reports] == ["lcov.info"]


def test_tested_sha_defaults_to_github_sha(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write(tmp_path, "lcov.info")
    monkeypatch.setenv("GITHUB_SHA", "b" * 40)

    assert coverage_request(["lcov.info"], root=tmp_path).tested_sha == "b" * 40
    assert coverage_request(["lcov.info"], tested_sha=SHA, root=tmp_path).tested_sha == SHA


@pytest.mark.parametrize("sha", [None, "", "abc123", "A" * 40, "a" * 41])
def test_missing_or_malformed_commit_is_refused(tmp_path: Path, sha: str | None) -> None:
    write(tmp_path, "lcov.info")

    with pytest.raises(ValueError, match="40-character"):
        coverage_request(["lcov.info"], tested_sha=sha, root=tmp_path)


def test_unusable_report_sets_are_refused(tmp_path: Path) -> None:
    write(tmp_path, "lcov.info")
    outside = write(tmp_path.parent, f"{tmp_path.name}-outside.info")

    with pytest.raises(ValueError, match="outside the report root"):
        coverage_request([outside], tested_sha=SHA, root=tmp_path)
    with pytest.raises(ValueError, match="more than once"):
        coverage_request(["lcov.info", "./lcov.info"], tested_sha=SHA, root=tmp_path)
    with pytest.raises(ValueError, match="1 to 50"):
        coverage_request([], tested_sha=SHA, root=tmp_path)
    with pytest.raises(ValueError, match="1 to 50"):
        names = [f"r{i}.info" for i in range(MAX_REPORTS + 1)]
        for name in names:
            write(tmp_path, name)
        coverage_request(names, tested_sha=SHA, root=tmp_path)
    with pytest.raises(TypeError, match="sequence"):
        coverage_request("lcov.info", tested_sha=SHA, root=tmp_path)
    with pytest.raises(FileNotFoundError):
        coverage_request(["missing.info"], tested_sha=SHA, root=tmp_path)


@MODES
async def test_upload_coverage_files_posts_the_files_for_the_commit(
    mode: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path, "python/lcov.info")
    monkeypatch.setenv("GITHUB_SHA", SHA)

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "POST"
        assert request.path == (
            f"/api/v1/organizations/{ORG}/repositories/{REPOSITORY}/coverage-reports"
        )
        assert json.loads(request.body) == {
            "tested_sha": SHA,
            "reports": [{"name": "python/lcov.info", "content": LCOV}],
        }
        return Reply(
            status=201,
            body={
                "report_id": str(REVIEW),
                "tested_sha": SHA,
                "created": True,
                "formats": ["LCOV"],
                "instrumented_lines": 2,
                "covered_lines": 1,
            },
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            result = client.upload_coverage_files(
                ORG, REPOSITORY, [Path("python/lcov.info")], root=tmp_path
            )
            if mode == "async":
                result = await result
        assert isinstance(result, CoverageUploadResponse)
        assert (result.created, result.covered_lines, result.instrumented_lines) == (True, 1, 2)
        assert len(server.requests) == 1


@MODES
async def test_invalid_input_sends_no_request(mode: str, tmp_path: Path) -> None:
    with Server(lambda request, index: Reply(status=500, body={})) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ValueError, match="40-character"):
                result = client.upload_coverage_files(ORG, REPOSITORY, ["lcov.info"])
                if mode == "async":
                    await result
        assert server.requests == []
