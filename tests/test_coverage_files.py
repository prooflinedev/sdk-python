from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from proofline import CoverageFile, CoverageUploadResponse
from proofline.coverage import MAX_BODY_BYTES, build_coverage_request

from .fixtures import ORG, REPOSITORY, REVIEW
from .http_server import Reply, Request, Server
from .test_http import MODES, call, session

SHA = "a" * 40
LCOV = "SF:src/main.py\nDA:1,1\nDA:2,0\nend_of_record\n"


def write(path: Path, text: str = LCOV) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def names(request: Any) -> list[str]:
    return [report.name for report in request.reports]


def test_reports_are_named_by_path_relative_to_root(tmp_path: Path) -> None:
    write(tmp_path / "coverage/lcov.info")
    write(tmp_path / "go/cover.out", "mode: set\n")
    request = build_coverage_request(
        SHA, ["coverage/lcov.info", tmp_path / "go/cover.out"], root=tmp_path
    )
    assert request.tested_sha == SHA
    assert names(request) == ["coverage/lcov.info", "go/cover.out"]
    assert request.reports[0].content == LCOV


def test_default_root_is_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(tmp_path / "lcov.info")
    monkeypatch.chdir(tmp_path)
    assert names(build_coverage_request(SHA, ["lcov.info"])) == ["lcov.info"]


def test_explicit_name_overrides_the_path(tmp_path: Path) -> None:
    write(tmp_path / "go/cover.out")
    request = build_coverage_request(
        SHA, [CoverageFile(tmp_path / "go/cover.out", "./go/coverage.out")], root=tmp_path
    )
    assert names(request) == ["go/coverage.out"]


@pytest.mark.parametrize("sha", ["a" * 7, "a" * 39, "A" * 41, "main", "g" * 40, ""])
def test_abbreviated_or_malformed_sha_is_refused(tmp_path: Path, sha: str) -> None:
    write(tmp_path / "lcov.info")
    with pytest.raises(ValueError, match="40 character"):
        build_coverage_request(sha, ["lcov.info"], root=tmp_path)


def test_report_count_must_be_one_to_fifty(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="1 to 50"):
        build_coverage_request(SHA, [], root=tmp_path)
    with pytest.raises(ValueError, match="1 to 50"):
        build_coverage_request(SHA, "lcov.info", root=tmp_path)
    files = [write(tmp_path / f"r{index}.info").name for index in range(51)]
    with pytest.raises(ValueError, match="1 to 50"):
        build_coverage_request(SHA, files, root=tmp_path)
    fifty = build_coverage_request(SHA, files[:50], root=tmp_path)
    assert len(fifty.reports) == 50


def test_duplicate_names_are_refused(tmp_path: Path) -> None:
    write(tmp_path / "a/lcov.info")
    write(tmp_path / "b/lcov.info")
    with pytest.raises(ValueError, match="used twice"):
        build_coverage_request(
            SHA,
            [
                "a/lcov.info",
                CoverageFile("b/lcov.info", "a/lcov.info"),
            ],
            root=tmp_path,
        )


def test_names_cannot_escape_the_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    write(tmp_path / "outside.info")
    write(root / "inside.info")
    with pytest.raises(ValueError, match="outside the root"):
        build_coverage_request(SHA, ["../outside.info"], root=root)
    with pytest.raises(ValueError, match="outside the root"):
        build_coverage_request(SHA, [tmp_path / "outside.info"], root=root)
    for name in ("../x.info", "/abs/x.info", "a/../../x.info", ""):
        with pytest.raises(ValueError, match="relative path"):
            build_coverage_request(SHA, [CoverageFile("inside.info", name)], root=root)


def test_a_symlink_out_of_the_root_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    target = write(tmp_path / "secret.txt", "token\n")
    (root / "lcov.info").symlink_to(target)
    with pytest.raises(ValueError, match="outside the root"):
        build_coverage_request(SHA, ["lcov.info"], root=root)


def test_non_utf8_report_is_refused(tmp_path: Path) -> None:
    (tmp_path / "lcov.info").write_bytes(b"SF:\xff\xfe\n")
    with pytest.raises(ValueError, match="not UTF-8"):
        build_coverage_request(SHA, ["lcov.info"], root=tmp_path)


def test_missing_file_raises_the_file_system_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_coverage_request(SHA, ["missing.info"], root=tmp_path)


def test_body_over_thirty_mebibytes_is_refused(tmp_path: Path) -> None:
    write(tmp_path / "big.info", "x" * (MAX_BODY_BYTES + 1))
    with pytest.raises(ValueError, match="30 MiB"):
        build_coverage_request(SHA, ["big.info"], root=tmp_path)


@MODES
async def test_upload_coverage_files_sends_the_named_reports(mode: str, tmp_path: Path) -> None:
    write(tmp_path / "python/lcov.info")

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
            result = await call(
                client,
                "upload_coverage_files",
                ORG,
                REPOSITORY,
                tested_sha=SHA,
                files=["python/lcov.info"],
                root=tmp_path,
            )
            assert isinstance(result, CoverageUploadResponse)
            assert (result.created, result.covered_lines, result.instrumented_lines) == (
                True,
                1,
                2,
            )
        assert len(server.requests) == 1


@MODES
async def test_invalid_files_send_nothing(mode: str, tmp_path: Path) -> None:
    with Server(lambda request, index: Reply(status=500, body={})) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(ValueError, match="40 character"):
                await call(
                    client,
                    "upload_coverage_files",
                    ORG,
                    REPOSITORY,
                    tested_sha="main",
                    files=["lcov.info"],
                    root=tmp_path,
                )
        assert server.requests == []
