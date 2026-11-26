"""Local Git changes as a patch review request, with the CLI's secret preflight.

`read_local_changes` builds the patch exactly as `proofline review` does: one Git snapshot
under fixed options, so personal Git configuration (prefixes, colour, external diff drivers,
copy detection, relative paths) cannot change what the server receives. Selected work-tree
bytes are collected in a copied index, so the repository's own index is never modified.

`check_secrets` refuses a patch that touches a `.env` path or carries a known credential shape
or private-key marker on any uploaded line, before any byte leaves the checkout. It recognizes
the CLI's listed shapes only; finding none says nothing else about the patch.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from uuid import UUID

from ._generated.models.patch_review_request import PatchReviewRequest
from ._generated.models.patch_trigger_source import PatchTriggerSource

LocalSelection = Literal["tracked", "staged", "untracked"]

MAX_PATCH_BYTES = 5 << 20
MAX_PATCH_FILES = 3_000
MAX_VERIFY_FINDINGS = 20
_SYMLINK = "120000"
_SUBMODULE = "160000"


class LocalChangesError(ValueError):
    """The local changes cannot be sent for review. Nothing was requested."""


class NoLocalChanges(LocalChangesError):
    """The selected local changes match their base, so there is nothing to review."""


class SecretInPatch(LocalChangesError):
    """An uploaded line or path matches a credential shape. The secret itself is never kept."""

    def __init__(
        self,
        message: str,
        *,
        path: str,
        kind: str,
        line: int | None = None,
        coordinate: str | None = None,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.kind = kind
        self.line = line
        self.coordinate = coordinate


@dataclass(frozen=True)
class PatchPath:
    """One changed file: `old` is None for an addition and `new` is None for a deletion."""

    old: str | None
    new: str | None


@dataclass(frozen=True)
class LocalPatch:
    """A patch against one exact base commit, as the server's patch review takes it."""

    base_commit_sha: str
    patch: str
    paths: tuple[PatchPath, ...] = field(repr=False)

    @property
    def files(self) -> int:
        return len(self.paths)

    def request(
        self,
        *,
        verify_finding_ids: Sequence[UUID] = (),
        trigger_source: PatchTriggerSource | None = None,
    ) -> PatchReviewRequest:
        """The request body for `request_patch_review`."""
        if isinstance(verify_finding_ids, (str, bytes)):
            raise ValueError("verify_finding_ids must be a list of finding UUIDs.")
        findings = [UUID(str(finding)) for finding in verify_finding_ids]
        if len(findings) > MAX_VERIFY_FINDINGS:
            raise ValueError(f"Re-verify at most {MAX_VERIFY_FINDINGS} findings in one request.")
        if trigger_source is not None:
            trigger_source = PatchTriggerSource(trigger_source)
        return PatchReviewRequest(
            base_commit_sha=self.base_commit_sha,
            patch=self.patch,
            trigger_source=trigger_source,
            verify_finding_ids=findings,
        )


# --------------------------------------------------------------------------- Git


def _git(root: Path, *args: str, index: Path | None = None) -> bytes:
    environment = dict(os.environ)
    # A hook may run beside a commit that holds index.lock; reads never take it.
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    if index is not None:
        environment["GIT_INDEX_FILE"] = str(index)
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            env=environment,
            check=False,
        )
    except OSError as error:
        raise LocalChangesError(f"Could not run git: {error}") from None
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", "replace").strip()
        raise LocalChangesError(f"git {args[0]} failed: {stderr}")
    return completed.stdout


def _line(root: Path, *args: str) -> str:
    return _git(root, *args).decode("utf-8", "replace").strip()


def _commit_sha(raw: str) -> str:
    sha = raw.strip().lower()
    if len(sha) not in (40, 64) or any(character not in "0123456789abcdef" for character in sha):
        raise LocalChangesError(f"{raw!r} is not a full commit SHA.")
    return sha


def _resolve(root: Path, revision: str) -> str:
    # A revision that starts with "-" would be read as an option.
    if not isinstance(revision, str) or not revision or revision.startswith("-"):
        raise LocalChangesError(f"{revision!r} names no commit in this checkout.")
    try:
        return _commit_sha(
            _line(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
        )
    except LocalChangesError:
        raise LocalChangesError(f"{revision!r} names no commit in this checkout.") from None


def _merge_base(root: Path, remote: str) -> str:
    for target in ("@{upstream}", f"refs/remotes/{remote}/HEAD"):
        try:
            _line(root, "rev-parse", "--verify", "--quiet", target)
        except LocalChangesError:
            continue
        return _commit_sha(_line(root, "merge-base", "HEAD", target))
    raise LocalChangesError(
        "The checkout has no base to review against: pass base=, set an upstream branch with "
        f"`git branch --set-upstream-to`, or run `git remote set-head {remote} --auto`."
    )


def _copy_index(root: Path, index: Path) -> None:
    current = _line(root, "rev-parse", "--path-format=absolute", "--git-path", "index")
    try:
        shutil.copyfile(current, index)
    except FileNotFoundError:
        pass  # A repository with nothing staged yet has no index.
    except OSError as error:
        raise LocalChangesError(f"Could not copy the Git index: {error}") from None


def _field(output: bytes, start: int) -> tuple[bytes, int]:
    end = output.find(b"\0", start)
    if end < 0:
        raise LocalChangesError("Could not read the patch's Git path metadata.")
    return output[start:end], end + 1


def _path(output: bytes, start: int) -> tuple[str, int]:
    raw, start = _field(output, start)
    if not raw:
        raise LocalChangesError("Could not read the patch's Git path metadata.")
    try:
        return raw.decode("utf-8"), start
    except UnicodeDecodeError:
        raise LocalChangesError(
            "A changed path is not UTF-8, which Proofline cannot review."
        ) from None


def _split_raw(output: bytes) -> tuple[list[PatchPath], bytes]:
    """Separates `--raw -z` records from the unchanged text patch that follows them."""
    paths: list[PatchPath] = []
    start = 0
    while start < len(output):
        header, start = _field(output, start)
        if not header:
            break
        fields = header.decode("ascii", "replace").split(" ")
        if not fields[0].startswith(":") or len(fields) != 5 or not fields[4]:
            raise LocalChangesError("Could not read the patch's Git path metadata.")
        modes, status = (fields[0][1:], fields[1]), fields[4][0]
        first, start = _path(output, start)
        if status == "U":
            raise LocalChangesError(f"{first!r} has an unresolved merge conflict.")
        if _SYMLINK in modes:
            raise LocalChangesError(
                f"{first!r} is a symbolic link; Proofline reviews text changes only."
            )
        if _SUBMODULE in modes:
            raise LocalChangesError(
                f"{first!r} is a submodule; Proofline reviews text changes only."
            )
        if status == "A":
            paths.append(PatchPath(None, first))
        elif status == "D":
            paths.append(PatchPath(first, None))
        elif status in "MT":
            paths.append(PatchPath(first, first))
        elif status == "R":
            second, start = _path(output, start)
            paths.append(PatchPath(first, second))
        else:
            raise LocalChangesError(f"{first!r} has a change Proofline cannot review ({status}).")
    return paths, output[start:]


def _lines(text: str) -> list[str]:
    """Lines as the CLI reads them: split on LF only, one trailing CR dropped per line."""
    parts = text.split("\n")
    if parts and parts[-1] == "":
        parts.pop()
    return [part[:-1] if part.endswith("\r") else part for part in parts]


def _diff(root: Path, base: str, head: str | None, index: Path | None) -> LocalPatch:
    args = [
        "--literal-pathspecs",
        "-c", "core.quotePath=false",
        # The server accepts renames and refuses copies, whatever local configuration asks.
        "-c", "diff.renames=true",
        "-c", "diff.suppressBlankEmpty=false",
        "diff",
    ]  # fmt: skip
    if head is None:
        args.append("--cached")
    args += [
        "--raw", "-z", "--patch", "--find-renames", "--no-relative", "--no-ext-diff",
        "--no-textconv", "--no-color", "--submodule=short", "--src-prefix=a/", "--dst-prefix=b/",
        base,
    ]  # fmt: skip
    if head is not None:
        args.append(head)
    args.append("--")
    paths, raw_patch = _split_raw(_git(root, *args, index=index))
    if len(raw_patch) > MAX_PATCH_BYTES:
        mebibytes = -(-len(raw_patch) // (1 << 20))
        raise LocalChangesError(
            f"The local changes make a {mebibytes} MiB patch; Proofline reviews up to 5 MiB."
        )
    if len(paths) > MAX_PATCH_FILES:
        raise LocalChangesError(
            f"The local changes include {len(paths)} files; Proofline reviews up to 3,000."
        )
    try:
        patch = raw_patch.decode("utf-8")
    except UnicodeDecodeError:
        raise LocalChangesError(
            "The local changes include text that is not UTF-8, which Proofline cannot review."
        ) from None
    blocks = 0
    in_header = False
    for line in _lines(patch):
        if line.startswith("diff --git "):
            blocks += 1
            in_header = True
        elif line.startswith("@@ "):
            in_header = False
        elif in_header and (line.startswith("Binary files ") or line == "GIT binary patch"):
            name = paths[blocks - 1].new or paths[blocks - 1].old if blocks <= len(paths) else "?"
            raise LocalChangesError(
                f"{name!r} is a binary change; Proofline reviews text changes only."
            )
    if blocks != len(paths):
        raise LocalChangesError("Could not read the patch's Git path metadata.")
    return LocalPatch(base, patch, tuple(paths))


def read_local_changes(
    cwd: str | os.PathLike[str] = ".",
    *,
    base: str | None = None,
    head: str | None = None,
    selection: LocalSelection = "tracked",
    remote: str = "origin",
) -> LocalPatch:
    """Build the patch `proofline review` would send for this checkout.

    Without `head`, `selection` picks the local bytes: "tracked" (the default) reads tracked
    work-tree files, staged or not; "staged" reads only the index; "untracked" also adds
    untracked files Git does not ignore. With `head`, only the committed range `base..head`
    is read. `base` defaults to the merge-base of HEAD with its upstream branch, or with
    `remote`'s default branch. Revisions resolve once to full commit SHAs.
    """
    if selection not in ("tracked", "staged", "untracked"):
        raise ValueError("selection must be tracked, staged or untracked.")
    if head is not None and (base is None or selection != "tracked"):
        raise ValueError("A committed range needs base and head, and takes no selection.")
    if not isinstance(remote, str) or not remote or remote.startswith("-") or "/" in remote:
        raise ValueError("remote must name one Git remote, such as origin.")
    try:
        root = Path(_line(Path(cwd), "rev-parse", "--show-toplevel"))
    except LocalChangesError as error:
        raise LocalChangesError(
            f"{os.fspath(cwd)!r} is not inside a Git checkout: {error}"
        ) from None
    if head is not None:
        assert base is not None
        return _diff(root, _resolve(root, base), _resolve(root, head), None)
    base_sha = _resolve(root, base) if base is not None else _merge_base(root, remote)
    with tempfile.TemporaryDirectory(prefix="proofline-index-") as scratch:
        index = Path(scratch) / "index"
        _copy_index(root, index)
        add = {"tracked": "--update", "staged": None, "untracked": "--all"}[selection]
        if add is not None:
            _git(root, "-c", "advice.addEmbeddedRepo=false", "add", add, index=index)
        return _diff(root, base_sha, None, index)


# ----------------------------------------------------------------- secret preflight


def _token_byte(character: str) -> bool:
    return character.isascii() and (character.isalnum() or character in "_-.")


def _alphanumeric(character: str) -> bool:
    return character.isascii() and character.isalnum()


def _upper_or_digit(character: str) -> bool:
    return character.isascii() and (character.isupper() or character.isdigit())


def _base32(character: str) -> bool:
    return character.isascii() and (character.isupper() or character in "234567")


@dataclass(frozen=True)
class _TokenShape:
    kind: str
    prefixes: tuple[str, ...]
    minimum: int
    body: Callable[[str], bool]


# The CLI's credential prefixes (src/preflight.rs). When two rows match, the first names it.
_TOKEN_SHAPES = (
    _TokenShape("an AWS access-key ID", ("AKIA", "ASIA"), 16, _upper_or_digit),
    _TokenShape("a GitHub token", ("ghp_", "gho_", "ghu_", "ghs_", "ghr_"), 36, _alphanumeric),
    _TokenShape("a GitHub token", ("github_pat_",), 82, _token_byte),
    _TokenShape("a GitHub token", ("ghs_",), 36, _token_byte),
    _TokenShape(
        "a Slack token",
        ("xoxb-", "xoxa-", "xoxp-", "xoxr-", "xoxs-", "xoxe-", "xoxe.", "xapp-"),
        8,
        _token_byte,
    ),
    _TokenShape("a Google API key", ("AIza",), 35, _token_byte),
    _TokenShape("a Stripe live key", ("sk_live_", "rk_live_"), 24, _alphanumeric),
    _TokenShape("a model-provider key", ("sk-",), 48, _alphanumeric),
    _TokenShape(
        "a model-provider key", ("sk-proj-", "sk-svcacct-", "sk-admin-", "sk-ant-"), 40, _token_byte
    ),
    _TokenShape("a Proofline token", ("plp_", "plo_", "pld_"), 52, _base32),
)


def _has_token(text: str, shape: _TokenShape) -> bool:
    for prefix in shape.prefixes:
        start = text.find(prefix)
        while start >= 0:
            body = text[start + len(prefix) : start + len(prefix) + shape.minimum]
            if len(body) == shape.minimum and all(shape.body(character) for character in body):
                return True
            start = text.find(prefix, start + len(prefix))
    return False


def secret_shape(text: str) -> str | None:
    """The kind of credential `text` carries, or None when it matches no listed shape."""
    if ("-----BEGIN " in text or "-----END " in text) and (
        "PRIVATE KEY-----" in text or "PRIVATE KEY BLOCK-----" in text
    ):
        return "a private-key marker"
    for shape in _TOKEN_SHAPES:
        if _has_token(text, shape):
            return shape.kind
    return None


def _hunk_start(field: str, prefix: str) -> int:
    if not field.startswith(prefix):
        raise LocalChangesError("Could not map the local patch to file paths and lines.")
    try:
        return int(field[1:].split(",")[0])
    except ValueError:
        raise LocalChangesError("Could not map the local patch to file paths and lines.") from None


def check_secrets(changes: LocalPatch, allow_paths: Sequence[str] = ()) -> None:
    """Refuse a patch that touches a `.env` path or carries a listed credential shape.

    Every uploaded line is read: added, removed and context lines, and hunk headings. A path in
    `allow_paths` (exact and repository-relative) is skipped. Raises `SecretInPatch` naming the
    path, line and kind of credential, never the credential itself.
    """
    if isinstance(allow_paths, (str, bytes)):
        raise ValueError("allow_paths must be a list of exact repository-relative paths.")
    allowed = list(allow_paths)
    for path in allowed:
        if (
            not isinstance(path, str)
            or path.startswith("/")
            or any(part in ("", ".", "..") for part in path.split("/"))
        ):
            raise ValueError(
                f"allow_paths entry {path!r} is not an exact repository-relative path."
            )
    files = iter(changes.paths)
    current: PatchPath | None = None
    old = new = 0
    in_hunk = False

    def inspect(path: str | None, line: int, coordinate: str, text: str) -> None:
        if path is None:
            raise LocalChangesError("Could not map the local patch to file paths and lines.")
        if path in allowed:
            return
        kind = secret_shape(text)
        if kind is not None:
            raise SecretInPatch(
                f"The local patch contains {kind} at {path!r}:{line} ({coordinate}); remove it "
                "before upload, or pass that exact path in allow_paths.",
                path=path,
                kind=kind,
                line=line,
                coordinate=coordinate,
            )

    for number, line in enumerate(_lines(changes.patch), start=1):
        if line.startswith("diff --git "):
            current = next(files, None)
            if current is None:
                raise LocalChangesError("Could not map the local patch to file paths and lines.")
            for changed in (current.old, current.new):
                if (
                    changed is not None
                    and changed not in allowed
                    and any(
                        part == ".env" or part.startswith(".env.") for part in changed.split("/")
                    )
                ):
                    raise SecretInPatch(
                        f"The local patch includes the sensitive .env path {changed!r}; remove it "
                        "before upload, or pass that exact path in allow_paths.",
                        path=changed,
                        kind="a .env path",
                    )
            in_hunk = False
            continue
        if current is None:
            raise LocalChangesError("Could not map the local patch to file paths and lines.")
        if line.startswith("@@ "):
            # A section heading can quote a line outside the hunk; name its patch line.
            inspect(current.new or current.old, number, "patch line", line)
            fields = line.split()
            if len(fields) < 4 or fields[0] != "@@" or fields[3] != "@@":
                raise LocalChangesError("Could not map the local patch to file paths and lines.")
            old, new = _hunk_start(fields[1], "-"), _hunk_start(fields[2], "+")
            in_hunk = True
        elif in_hunk:
            if line.startswith("+"):
                inspect(current.new, new, "new line", line[1:])
                new += 1
            elif line.startswith("-"):
                inspect(current.old, old, "base line", line[1:])
                old += 1
            elif line.startswith(" "):
                inspect(current.new or current.old, new, "new line", line[1:])
                old += 1
                new += 1
            elif not line.startswith("\\ No newline at end of file"):
                raise LocalChangesError("Could not map the local patch to file paths and lines.")
    if next(files, None) is not None:
        raise LocalChangesError("Could not map the local patch to file paths and lines.")


def patch_review_request_from_git(
    cwd: str | os.PathLike[str] = ".",
    *,
    base: str | None = None,
    head: str | None = None,
    selection: LocalSelection = "tracked",
    remote: str = "origin",
    allow_paths: Sequence[str] = (),
    verify_finding_ids: Sequence[UUID] = (),
    trigger_source: PatchTriggerSource | None = None,
) -> PatchReviewRequest:
    """Read, check and package local changes. Raises before anything is sent."""
    changes = read_local_changes(cwd, base=base, head=head, selection=selection, remote=remote)
    if not changes.files:
        raise NoLocalChanges(
            f"Nothing to review: the selected local changes match {changes.base_commit_sha}."
        )
    check_secrets(changes, allow_paths)
    return changes.request(verify_finding_ids=verify_finding_ids, trigger_source=trigger_source)
