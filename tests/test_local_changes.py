from __future__ import annotations

import inspect
import json
import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from pydantic import SecretStr

from proofline import (
    AsyncProoflineClient,
    LocalChangesError,
    LocalPatch,
    NoLocalChanges,
    PatchPath,
    ProoflineClient,
    ProoflineError,
    SecretInPatch,
    check_secrets,
    read_local_changes,
)
from proofline import local_changes as local_module
from proofline._generated.models.patch_trigger_source import PatchTriggerSource

from .fixtures import ORG, REPOSITORY, REVIEW, TOKEN
from .http_server import Reply, Request, Server

MODES = pytest.mark.parametrize("mode", ["sync", "async"])
Client = ProoflineClient | AsyncProoflineClient
FINDING = UUID("00000000-0000-4000-8000-0000000000f1")


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "sdk@example.invalid")
    git(root, "config", "user.name", "SDK test")
    git(root, "config", "commit.gpgsign", "false")
    (root / "keep.txt").write_text("one\ntwo\n")
    (root / "old.txt").write_text("rename me\n" * 8)
    (root / "gone.txt").write_text("going\n")
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("print('hi')\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    return root


def head_of(root: Path) -> str:
    return git(root, "rev-parse", "HEAD")


def paths(patch: LocalPatch) -> list[tuple[str | None, str | None]]:
    return [(path.old, path.new) for path in patch.paths]


# A credential built at run time, so this file never contains one literally.
def credential(prefix: str, body: str) -> str:
    return "".join([prefix, body])


# ----------------------------------------------------------------------------- git


def test_selections_pick_their_bytes_and_leave_the_index_unchanged(repo: Path) -> None:
    (repo / "keep.txt").write_text("one\ntwo\nthree\n")
    git(repo, "mv", "old.txt", "new.txt")
    (repo / "gone.txt").unlink()
    (repo / "added.txt").write_text("staged\n")
    git(repo, "add", "added.txt")
    (repo / "loose.txt").write_text("untracked\n")
    index = (repo / ".git" / "index").read_bytes()

    tracked = read_local_changes(repo, base="HEAD")
    staged = read_local_changes(repo, base="HEAD", selection="staged")
    untracked = read_local_changes(repo, base="HEAD", selection="untracked")

    assert paths(tracked) == [
        (None, "added.txt"),
        ("gone.txt", None),
        ("keep.txt", "keep.txt"),
        ("old.txt", "new.txt"),
    ]
    assert paths(staged) == [(None, "added.txt"), ("old.txt", "new.txt")]
    # Git orders files by path, so the untracked file sorts before the rename's new name.
    assert paths(untracked) == [
        (None, "added.txt"),
        ("gone.txt", None),
        ("keep.txt", "keep.txt"),
        (None, "loose.txt"),
        ("old.txt", "new.txt"),
    ]
    assert tracked.base_commit_sha == head_of(repo)
    assert (repo / ".git" / "index").read_bytes() == index


def test_personal_git_configuration_cannot_change_the_patch(repo: Path) -> None:
    for key, value in {
        "diff.noprefix": "true",
        "diff.mnemonicPrefix": "true",
        "color.ui": "always",
        "color.diff": "always",
        "diff.relative": "true",
        "diff.renames": "copies",
        "diff.external": "this-command-does-not-exist",
        "core.quotePath": "true",
    }.items():
        git(repo, "config", key, value)
    (repo / "copy.txt").write_text((repo / "old.txt").read_text())
    (repo / "src" / "app.py").write_text("print('changed')\n")
    (repo / "naïve.txt").write_text("unicode path\n")
    git(repo, "add", "-A")

    patch = read_local_changes(repo / "src", base="HEAD")

    assert "\x1b[" not in patch.patch
    assert "copy from" not in patch.patch
    assert "diff --git a/src/app.py b/src/app.py" in patch.patch
    assert "diff --git a/naïve.txt b/naïve.txt" in patch.patch
    assert paths(patch) == [(None, "copy.txt"), (None, "naïve.txt"), ("src/app.py", "src/app.py")]


def test_default_base_is_the_merge_base_with_the_remote_default_branch(repo: Path) -> None:
    base = head_of(repo)
    git(repo, "update-ref", "refs/remotes/origin/main", base)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    (repo / "keep.txt").write_text("committed locally\n")
    git(repo, "commit", "-q", "-am", "local work")
    (repo / "src" / "app.py").write_text("print('uncommitted')\n")

    patch = read_local_changes(repo)

    assert patch.base_commit_sha == base
    assert paths(patch) == [("keep.txt", "keep.txt"), ("src/app.py", "src/app.py")]


def test_upstream_branch_wins_over_the_remote_default(repo: Path) -> None:
    first = head_of(repo)
    (repo / "keep.txt").write_text("upstream moved\n")
    git(repo, "commit", "-q", "-am", "upstream")
    upstream = head_of(repo)
    git(repo, "update-ref", "refs/remotes/origin/main", first)
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    git(repo, "update-ref", "refs/remotes/origin/feature", upstream)
    git(repo, "config", "remote.origin.url", "https://example.invalid/owner/name.git")
    git(repo, "config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
    git(repo, "config", "branch.main.remote", "origin")
    git(repo, "config", "branch.main.merge", "refs/heads/feature")

    assert read_local_changes(repo).base_commit_sha == upstream


def test_a_checkout_without_any_base_is_refused(repo: Path) -> None:
    with pytest.raises(LocalChangesError, match="no base to review against"):
        read_local_changes(repo)


def test_a_committed_range_ignores_the_work_tree(repo: Path) -> None:
    base = head_of(repo)
    (repo / "keep.txt").write_text("committed\n")
    git(repo, "commit", "-q", "-am", "change")
    (repo / "src" / "app.py").write_text("print('not committed')\n")

    patch = read_local_changes(repo, base=base, head="HEAD")

    assert patch.base_commit_sha == base
    assert paths(patch) == [("keep.txt", "keep.txt")]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"head": "HEAD"},
        {"base": "HEAD", "head": "HEAD", "selection": "staged"},
        {"selection": "everything"},
        {"remote": "-x"},
        {"remote": "origin/main"},
    ],
)
def test_contradictory_arguments_are_refused(repo: Path, kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        read_local_changes(repo, **kwargs)


@pytest.mark.parametrize("revision", ["", "-p", "--output=x", "no-such-branch"])
def test_unknown_or_option_like_revisions_are_refused(repo: Path, revision: str) -> None:
    with pytest.raises(LocalChangesError, match="names no commit"):
        read_local_changes(repo, base=revision)


def test_a_directory_outside_any_checkout_is_refused(tmp_path: Path) -> None:
    with pytest.raises(LocalChangesError, match="not inside a Git checkout"):
        read_local_changes(tmp_path, base="HEAD")


def test_binary_changes_are_refused(repo: Path) -> None:
    (repo / "image.bin").write_bytes(b"\x00\x01\x02\x03binary")
    git(repo, "add", "image.bin")
    with pytest.raises(LocalChangesError, match="'image.bin' is a binary change"):
        read_local_changes(repo, base="HEAD")


def test_symbolic_links_and_submodules_are_refused(repo: Path) -> None:
    blob = subprocess.run(
        ["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
        input="keep.txt",
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"120000,{blob},link")
    with pytest.raises(LocalChangesError, match="'link' is a symbolic link"):
        read_local_changes(repo, base="HEAD", selection="staged")
    git(repo, "rm", "-q", "--cached", "link")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{head_of(repo)},vendor/lib")
    with pytest.raises(LocalChangesError, match="'vendor/lib' is a submodule"):
        read_local_changes(repo, base="HEAD", selection="staged")


def test_unresolved_merge_conflicts_are_refused(repo: Path) -> None:
    git(repo, "checkout", "-q", "-b", "other")
    (repo / "keep.txt").write_text("theirs\n")
    git(repo, "commit", "-q", "-am", "theirs")
    git(repo, "checkout", "-q", "main")
    (repo / "keep.txt").write_text("ours\n")
    git(repo, "commit", "-q", "-am", "ours")
    subprocess.run(["git", "-C", str(repo), "merge", "-q", "other"], capture_output=True)
    with pytest.raises(LocalChangesError, match="'keep.txt' has an unresolved merge conflict"):
        read_local_changes(repo, base="HEAD", selection="staged")


def test_text_that_is_not_utf8_is_refused(repo: Path) -> None:
    (repo / "keep.txt").write_bytes("café\n".encode("latin-1"))
    with pytest.raises(LocalChangesError, match="not UTF-8"):
        read_local_changes(repo, base="HEAD")


def test_patch_size_and_file_count_limits(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (repo / "keep.txt").write_text("x\n" * 200)
    (repo / "src" / "app.py").write_text("y\n")
    monkeypatch.setattr(local_module, "MAX_PATCH_BYTES", 100)
    with pytest.raises(LocalChangesError, match="up to 5 MiB"):
        read_local_changes(repo, base="HEAD")
    monkeypatch.setattr(local_module, "MAX_PATCH_BYTES", 5 << 20)
    monkeypatch.setattr(local_module, "MAX_PATCH_FILES", 1)
    with pytest.raises(LocalChangesError, match="2 files"):
        read_local_changes(repo, base="HEAD")


def test_no_changes_reads_as_an_empty_patch(repo: Path) -> None:
    patch = read_local_changes(repo, base="HEAD")
    assert (patch.files, patch.patch) == (0, "")


def test_request_carries_findings_and_trigger_and_bounds_findings(repo: Path) -> None:
    (repo / "keep.txt").write_text("changed\n")
    patch = read_local_changes(repo, base="HEAD")
    body = patch.request(
        verify_finding_ids=[FINDING], trigger_source=PatchTriggerSource.HOOK_PRE_PUSH
    )
    assert body.to_dict() == {
        "base_commit_sha": head_of(repo),
        "patch": patch.patch,
        "trigger_source": "HOOK_PRE_PUSH",
        "verify_finding_ids": [str(FINDING)],
    }
    with pytest.raises(ValueError, match="at most 20"):
        patch.request(verify_finding_ids=[FINDING] * 21)


# -------------------------------------------------------------------- secret check

SHAPES = [
    ("AKIA", "A1B2C3D4E5F6G7H8", "an AWS access-key ID"),
    ("ghp_", "a" * 36, "a GitHub token"),
    ("github_pat_", "a" * 82, "a GitHub token"),
    ("xoxb-", "12345678", "a Slack token"),
    ("AIza", "a" * 35, "a Google API key"),
    ("sk_live_", "a" * 24, "a Stripe live key"),
    ("sk-", "a" * 48, "a model-provider key"),
    ("sk-ant-", "a" * 40, "a model-provider key"),
    ("plp_", "A" * 52, "a Proofline token"),
]


def one_file(
    lines: list[str], *, old: str | None = "app.py", new: str | None = "app.py"
) -> LocalPatch:
    header = f"diff --git a/{old or new} b/{new or old}\n--- a/{old}\n+++ b/{new}\n"
    return LocalPatch("a" * 40, header + "\n".join(lines) + "\n", (PatchPath(old, new),))


@pytest.mark.parametrize(("prefix", "body", "kind"), SHAPES)
def test_each_listed_credential_shape_is_refused_at_its_minimum(
    prefix: str, body: str, kind: str
) -> None:
    patch = one_file(["@@ -1,0 +1,1 @@", "+key = " + credential(prefix, body)])
    with pytest.raises(SecretInPatch) as caught:
        check_secrets(patch)
    assert (caught.value.kind, caught.value.path, caught.value.line) == (kind, "app.py", 1)
    assert credential(prefix, body) not in str(caught.value)


@pytest.mark.parametrize(("prefix", "body", "kind"), SHAPES)
def test_a_body_one_short_of_the_minimum_is_not_a_credential(
    prefix: str, body: str, kind: str
) -> None:
    check_secrets(one_file(["@@ -1,0 +1,1 @@", "+key = " + credential(prefix, body[:-1])]))


def test_private_key_markers_are_refused_but_certificates_are_not() -> None:
    marker = "-----" + "BEGIN RSA PRIVATE KEY" + "-----"
    with pytest.raises(SecretInPatch, match="a private-key marker"):
        check_secrets(one_file(["@@ -1,0 +1,1 @@", "+" + marker]))
    check_secrets(one_file(["@@ -1,0 +1,1 @@", "+-----BEGIN CERTIFICATE-----"]))


def test_removed_context_and_heading_lines_are_uploaded_so_they_are_read() -> None:
    token = credential("ghp_", "b" * 36)
    cases = [
        (["@@ -3,1 +3,0 @@", "-" + token], "base line", 3),
        (["@@ -7,2 +7,2 @@", " " + token, "+x"], "new line", 7),
        ([f"@@ -1,1 +1,1 @@ def handler({token}):", "+x"], "patch line", 4),
    ]
    for lines, coordinate, line in cases:
        with pytest.raises(SecretInPatch) as caught:
            check_secrets(one_file(lines))
        assert (caught.value.coordinate, caught.value.line) == (coordinate, line)


def test_line_numbers_follow_each_hunk() -> None:
    token = credential("AKIA", "Z" * 16)
    patch = one_file(["@@ -1,2 +1,2 @@", " a", "-b", "+c", "@@ -10,1 +10,2 @@", " d", "+" + token])
    with pytest.raises(SecretInPatch) as caught:
        check_secrets(patch)
    assert caught.value.line == 11


@pytest.mark.parametrize("path", [".env", "config/.env", ".env.local", "deploy/.env.production"])
def test_env_paths_are_refused_unless_allowed(path: str) -> None:
    patch = one_file(["@@ -0,0 +1,1 @@", "+X=1"], old=None, new=path)
    with pytest.raises(SecretInPatch, match="sensitive .env path"):
        check_secrets(patch)
    check_secrets(patch, allow_paths=[path])


def test_similar_names_are_not_env_paths() -> None:
    for path in (".envrc", "env.example", "docs/environment.md"):
        check_secrets(one_file(["@@ -0,0 +1,1 @@", "+X=1"], old=None, new=path))


def test_allow_paths_skips_only_that_exact_path() -> None:
    token = credential("ghp_", "c" * 36)
    check_secrets(one_file(["@@ -1,0 +1,1 @@", "+" + token]), allow_paths=["app.py"])
    with pytest.raises(SecretInPatch):
        check_secrets(one_file(["@@ -1,0 +1,1 @@", "+" + token]), allow_paths=["other.py"])


@pytest.mark.parametrize("bad", ["/app.py", "../app.py", "a//b", "./app.py", ""])
def test_allow_paths_must_be_exact_repository_relative_paths(bad: str) -> None:
    with pytest.raises(ValueError, match="allow_paths"):
        check_secrets(one_file(["@@ -1,0 +1,1 @@", "+x"]), allow_paths=[bad])


def test_a_patch_that_does_not_match_its_paths_is_refused() -> None:
    broken = LocalPatch("a" * 40, "diff --git a/x b/x\n@@ nonsense @@\n", (PatchPath("x", "x"),))
    with pytest.raises(LocalChangesError, match="Could not map"):
        check_secrets(broken)
    missing = LocalPatch("a" * 40, "diff --git a/x b/x\n", ())
    with pytest.raises(LocalChangesError, match="Could not map"):
        check_secrets(missing)


def test_a_secret_written_to_a_real_checkout_is_refused_before_upload(repo: Path) -> None:
    (repo / "src" / "app.py").write_text("token = '" + credential("xoxb-", "99887766") + "'\n")
    with pytest.raises(SecretInPatch) as caught:
        check_secrets(read_local_changes(repo, base="HEAD"))
    assert (caught.value.path, caught.value.line, caught.value.kind) == (
        "src/app.py",
        1,
        "a Slack token",
    )


# ------------------------------------------------------------------------- clients


@asynccontextmanager
async def session(mode: str, url: str) -> AsyncIterator[Client]:
    if mode == "sync":
        with ProoflineClient(SecretStr(TOKEN), base_url=url) as client:
            yield client
    else:
        async with AsyncProoflineClient(SecretStr(TOKEN), base_url=url) as async_client:
            yield async_client


async def review_from_git(client: Client, **kwargs: Any) -> Any:
    result = client.request_patch_review_from_git(ORG, REPOSITORY, **kwargs)
    return await result if inspect.isawaitable(result) else result


@MODES
async def test_clients_post_the_checkout_patch(mode: str, repo: Path) -> None:
    (repo / "keep.txt").write_text("one\ntwo\nthree\n")
    expected = read_local_changes(repo, base="HEAD")

    def respond(request: Request, index: int) -> Reply:
        assert request.method == "POST"
        assert (
            request.path == f"/api/v1/organizations/{ORG}/repositories/{REPOSITORY}/patch-reviews"
        )
        assert json.loads(request.body) == {
            "base_commit_sha": expected.base_commit_sha,
            "patch": expected.patch,
            "trigger_source": "HOOK_PRE_COMMIT",
            "verify_finding_ids": [str(FINDING)],
        }
        return Reply(
            body={
                "review_id": str(REVIEW),
                "existing": False,
                "patch_digest": "b" * 64,
                "verify": [],
            }
        )

    with Server(respond) as server:
        async with session(mode, server.url) as client:
            result = await review_from_git(
                client,
                cwd=repo,
                base="HEAD",
                verify_finding_ids=[FINDING],
                trigger_source=PatchTriggerSource.HOOK_PRE_COMMIT,
            )
        assert (result.review_id, result.existing) == (REVIEW, False)
        assert len(server.requests) == 1


@MODES
async def test_clients_send_nothing_when_the_checkout_is_refused(mode: str, repo: Path) -> None:
    with Server(lambda request, index: Reply(status=500)) as server:
        async with session(mode, server.url) as client:
            with pytest.raises(NoLocalChanges):
                await review_from_git(client, cwd=repo, base="HEAD")
            (repo / "src" / "app.py").write_text(credential("sk-proj-", "d" * 40) + "\n")
            with pytest.raises(SecretInPatch):
                await review_from_git(client, cwd=repo, base="HEAD")
            # Allowed, so it is sent; this test server answers every request with 500.
            with pytest.raises(ProoflineError):
                await review_from_git(client, cwd=repo, base="HEAD", allow_paths=["src/app.py"])
        assert len(server.requests) == 1


def test_sync_and_async_review_from_git_share_one_signature() -> None:
    sync_parameters = inspect.signature(ProoflineClient.request_patch_review_from_git).parameters
    async_method = AsyncProoflineClient.request_patch_review_from_git
    assert inspect.iscoroutinefunction(async_method)
    assert sync_parameters == inspect.signature(async_method).parameters
