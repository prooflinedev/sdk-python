"""GitHub Actions OIDC authentication, event context, and workflow annotations."""

from __future__ import annotations

import ipaddress
import json
import os
import re
import threading
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from time import monotonic
from typing import TYPE_CHECKING, Any, Literal, Self
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import UUID

import anyio
import httpx2
from pydantic import SecretStr

from . import _transport
from .outcomes import _WITHHELD_MARKER, ReviewOutcome, _code_assessment

if TYPE_CHECKING:
    from ._generated.models.customer_evidence_ref import CustomerEvidenceRef
    from ._generated.models.customer_finding import CustomerFinding
    from ._generated.models.customer_review_detail import CustomerReviewDetail

_DEFAULT_BASE_URL = "https://proofline.sh"
_DEFAULT_AUDIENCE = "proofline"
_MAX_EVENT_BYTES = 10 * 1024 * 1024
_RENEWAL_LEAD_SECONDS = 60.0
_CLOSED_LIFECYCLES = frozenset({"RESOLVED", "DISMISSED", "ACCEPTED_RISK"})
_SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_BIDI_CODEPOINTS = frozenset(
    {0x061C, *range(0x200E, 0x2010), *range(0x202A, 0x202F), *range(0x2066, 0x206A)}
)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _is_loopback_host(hostname: str) -> bool:
    try:
        return ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        return False


def _validate_audience(audience: str) -> str:
    if (
        not audience
        or audience != audience.strip()
        or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in audience)
    ):
        raise ValueError(
            "GitHub Actions OIDC audience must be a nonempty string without whitespace."
        )
    return audience


def _validate_oidc_request_url(raw: str) -> str:
    if not raw or raw != raw.strip() or any(ord(ch) < 32 or ord(ch) == 127 for ch in raw):
        raise ValueError("ACTIONS_ID_TOKEN_REQUEST_URL must be an HTTPS or literal loopback URL.")
    try:
        parts = urlsplit(raw)
        if (
            not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.fragment
        ):
            raise ValueError
        scheme = parts.scheme.lower()
        loopback = _is_loopback_host(parts.hostname)
        if scheme != "https" and not (scheme == "http" and loopback):
            raise ValueError
        parts.port
        httpx2.URL(raw)
    except (ValueError, httpx2.InvalidURL):
        raise ValueError(
            "ACTIONS_ID_TOKEN_REQUEST_URL must be an HTTPS or literal loopback URL."
        ) from None
    return raw


def _oidc_url_with_audience(request_url: str, audience: str) -> str:
    parts = urlsplit(request_url)
    pairs = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k != "audience"]
    pairs.append(("audience", audience))
    path = parts.path or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc, path, urlencode(pairs), ""))


def _url_without_query(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme.lower()}://{parts.netloc}{parts.path or '/'}"


def _resolve_base_url(base_url: str | None, env: Mapping[str, str]) -> str:
    if base_url is not None:
        return _transport.base_url(base_url)
    configured = env.get("PROOFLINE_BASE_URL", "")
    return _transport.base_url(configured if configured else _DEFAULT_BASE_URL)


def _require_actions_environment(
    *,
    base_url: str | None,
    audience: str,
    timeout: float,
    environ: Mapping[str, str] | None,
) -> tuple[str, str, SecretStr, str, float]:
    env = os.environ if environ is None else environ
    if env.get("GITHUB_ACTIONS") != "true":
        raise ValueError("GitHub Actions OIDC exchange requires GITHUB_ACTIONS=true.")
    request_url = _validate_oidc_request_url(env.get("ACTIONS_ID_TOKEN_REQUEST_URL", ""))
    request_token = _transport.validate_token(
        env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", ""),
        error_message="ACTIONS_ID_TOKEN_REQUEST_TOKEN is required for GitHub Actions OIDC.",
    )
    resolved_base = _resolve_base_url(base_url, env)
    validated_audience = _validate_audience(audience)
    validated_timeout = _transport.validate_timeout(timeout)
    return resolved_base, request_url, request_token, validated_audience, validated_timeout


def _is_json_response(response: httpx2.Response) -> bool:
    content_type = response.headers.get("content-type", "")
    media = content_type.split(";", 1)[0].strip().lower()
    return media == "application/json"


def _parse_oidc_token(response: httpx2.Response, request_url: str) -> SecretStr:
    if not 200 <= response.status_code < 300:
        raise _transport.ProoflineError(
            response.status_code,
            "urn:proofline:sdk:oidc-error",
            f"GitHub Actions OIDC token request failed for {_url_without_query(request_url)} "
            f"with status {response.status_code}.",
        )
    if not _is_json_response(response):
        raise _transport.invalid_response()
    try:
        payload = response.json()
    except (ValueError, UnicodeError):
        raise _transport.invalid_response() from None
    if not isinstance(payload, dict) or not isinstance(payload.get("value"), str):
        raise _transport.invalid_response()
    try:
        return _transport.validate_token(
            payload["value"],
            error_message="GitHub Actions OIDC token value is invalid.",
        )
    except ValueError:
        raise _transport.invalid_response() from None


def _parse_lease_response(
    response: httpx2.Response,
    secrets: tuple[SecretStr, ...],
) -> GitHubActionsLease:
    if not 200 <= response.status_code < 300:
        raise _transport.problem(response, secrets)
    if not _is_json_response(response):
        raise _transport.invalid_response()
    try:
        payload = response.json()
    except (ValueError, UnicodeError):
        raise _transport.invalid_response() from None
    if not isinstance(payload, dict):
        raise _transport.invalid_response()
    raw_token = payload.get("token")
    raw_org = payload.get("organization_id")
    raw_expires = payload.get("expires_at")
    raw_repo = payload.get("repository_id")
    raw_scope = payload.get("scope")
    if (
        not isinstance(raw_token, str)
        or not isinstance(raw_org, str)
        or not isinstance(raw_expires, str)
        or (raw_repo is not None and not isinstance(raw_repo, str))
        or (raw_scope is not None and not isinstance(raw_scope, str))
    ):
        raise _transport.invalid_response()
    try:
        token = _transport.validate_token(raw_token)
        organization_id = UUID(raw_org)
        repository_id = UUID(raw_repo) if raw_repo is not None else None
        expires_at = datetime.fromisoformat(raw_expires)
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must include timezone offset")
        expires_at = expires_at.astimezone(UTC)
    except ValueError:
        raise _transport.invalid_response() from None
    return GitHubActionsLease(
        token=token,
        organization_id=organization_id,
        expires_at=expires_at,
        repository_id=repository_id,
        scope=raw_scope,
    )


def _compute_renew_at(
    start_monotonic: float,
    now_utc: datetime,
    expires_at: datetime,
) -> float:
    ttl = max(0.0, (expires_at - now_utc).total_seconds())
    lead = min(_RENEWAL_LEAD_SECONDS, ttl / 2.0)
    return start_monotonic + max(0.0, ttl - lead)


def _transport_exception(error: httpx2.HTTPError, target_label: str) -> _transport.ProoflineError:
    if isinstance(error, httpx2.TimeoutException):
        return _transport.timeout_error()
    return _transport.ProoflineError(
        0,
        "urn:proofline:sdk:transport",
        f"GitHub Actions credential exchange failed for {target_label} ({type(error).__name__}).",
    )


@dataclass(frozen=True, slots=True)
class GitHubActionsLease:
    """Short-lived Proofline credential issued from a GitHub Actions OIDC exchange."""

    token: SecretStr
    organization_id: UUID
    expires_at: datetime
    repository_id: UUID | None = None
    scope: str | None = None


@dataclass(frozen=True, slots=True)
class _ActiveLease:
    lease: GitHubActionsLease
    renew_at: float


class _CredentialState:
    """Shared validation, secret tracking, and renewal scheduling for sync/async holders."""

    def __init__(
        self,
        *,
        base_url: str,
        request_url: str,
        request_token: SecretStr,
        audience: str,
        timeout: float,
        monotonic_clock: Callable[[], float],
        utc_now: Callable[[], datetime],
    ) -> None:
        self.base_url = _transport.base_url(base_url)
        self.request_url = _oidc_url_with_audience(
            _validate_oidc_request_url(request_url),
            _validate_audience(audience),
        )
        self.request_token = _transport.validate_token(
            request_token,
            error_message="ACTIONS_ID_TOKEN_REQUEST_TOKEN is required for GitHub Actions OIDC.",
        )
        self.audience = audience
        self.timeout = _transport.validate_timeout(timeout)
        self.monotonic_clock = monotonic_clock
        self.utc_now = utc_now
        self.exchange_url = f"{self.base_url}/api/v1/ci/github-actions/credentials"
        self.active: _ActiveLease | None = None
        self._retired: deque[SecretStr] = deque(maxlen=16)

    def current_if_fresh(self) -> SecretStr | None:
        if self.active is not None and self.monotonic_clock() < self.active.renew_at:
            return self.active.lease.token
        return None

    def record(self, lease: GitHubActionsLease, start_mono: float) -> GitHubActionsLease:
        if self.active is not None and lease.organization_id != self.active.lease.organization_id:
            raise _transport.ProoflineError(
                0,
                "urn:proofline:sdk:credential-mismatch",
                "Renewed GitHub Actions credential returned a different organization_id.",
            )
        if self.active is not None:
            self._retired.append(self.active.lease.token)
        renew_at = _compute_renew_at(start_mono, self.utc_now(), lease.expires_at)
        self.active = _ActiveLease(lease=lease, renew_at=renew_at)
        return lease

    def remember_secret(self, secret: SecretStr) -> None:
        self._retired.append(secret)

    def secrets(self) -> tuple[SecretStr, ...]:
        items: list[SecretStr] = [self.request_token, *self._retired]
        if self.active is not None:
            items.append(self.active.lease.token)
        return tuple(items)


def _client_headers() -> dict[str, str]:
    return {
        "User-Agent": f"proofline-python/{_transport.VERSION}",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
    }


class GitHubActionsCredentials:
    """Synchronous secretless credential provider backed by GitHub Actions OIDC."""

    def __init__(
        self,
        *,
        request_url: str,
        request_token: str | SecretStr,
        base_url: str = _DEFAULT_BASE_URL,
        audience: str = _DEFAULT_AUDIENCE,
        timeout: float = 30.0,
        monotonic_clock: Callable[[], float] = monotonic,
        utc_now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._state = _CredentialState(
            base_url=base_url,
            request_url=request_url,
            request_token=_transport.validate_token(
                request_token,
                error_message="ACTIONS_ID_TOKEN_REQUEST_TOKEN is required for GitHub Actions OIDC.",
            ),
            audience=audience,
            timeout=timeout,
            monotonic_clock=monotonic_clock,
            utc_now=utc_now,
        )
        self._lock = threading.Lock()
        self._http = httpx2.Client(
            headers=_client_headers(),
            timeout=httpx2.Timeout(self._state.timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.SingleAttemptTransport(self._state.timeout),
        )

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str | None = None,
        audience: str = _DEFAULT_AUDIENCE,
        timeout: float = 30.0,
        environ: Mapping[str, str] | None = None,
        monotonic_clock: Callable[[], float] = monotonic,
        utc_now: Callable[[], datetime] = _utc_now,
    ) -> Self:
        resolved_base, request_url, request_token, validated_audience, validated_timeout = (
            _require_actions_environment(
                base_url=base_url,
                audience=audience,
                timeout=timeout,
                environ=environ,
            )
        )
        return cls(
            request_url=request_url,
            request_token=request_token,
            base_url=resolved_base,
            audience=validated_audience,
            timeout=validated_timeout,
            monotonic_clock=monotonic_clock,
            utc_now=utc_now,
        )

    @property
    def base_url(self) -> str:
        return self._state.base_url

    @property
    def lease(self) -> GitHubActionsLease | None:
        with self._lock:
            return None if self._state.active is None else self._state.active.lease

    @property
    def organization_id(self) -> UUID | None:
        current = self.lease
        return None if current is None else current.organization_id

    @property
    def repository_id(self) -> UUID | None:
        current = self.lease
        return None if current is None else current.repository_id

    def secrets(self) -> tuple[SecretStr, ...]:
        with self._lock:
            return self._state.secrets()

    def token(self) -> SecretStr:
        with self._lock:
            cached = self._state.current_if_fresh()
            if cached is not None:
                return cached
            return self._exchange_locked().token

    def exchange(self) -> GitHubActionsLease:
        with self._lock:
            return self._exchange_locked()

    def _exchange_locked(self) -> GitHubActionsLease:
        start_mono = self._state.monotonic_clock()
        oidc_jwt = self._fetch_oidc_token()
        self._state.remember_secret(oidc_jwt)
        lease = self._exchange_for_lease(oidc_jwt)
        return self._state.record(lease, start_mono)

    def _fetch_oidc_token(self) -> SecretStr:
        label = _url_without_query(self._state.request_url)
        try:
            with self._http.stream(
                "GET",
                self._state.request_url,
                headers={"Authorization": f"Bearer {self._state.request_token.get_secret_value()}"},
            ) as response:
                response.read()
                return _parse_oidc_token(response, self._state.request_url)
        except _transport.ProoflineError:
            raise
        except httpx2.HTTPError as error:
            raise _transport_exception(error, label) from None

    def _exchange_for_lease(self, oidc_jwt: SecretStr) -> GitHubActionsLease:
        try:
            with self._http.stream(
                "POST",
                self._state.exchange_url,
                headers={"Authorization": f"Bearer {oidc_jwt.get_secret_value()}"},
            ) as response:
                response.read()
                return _parse_lease_response(response, self._state.secrets())
        except _transport.ProoflineError:
            raise
        except httpx2.HTTPError as error:
            raise _transport_exception(error, self._state.exchange_url) from None

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"GitHubActionsCredentials(base_url={self._state.base_url!r})"


class AsyncGitHubActionsCredentials:
    """Asynchronous secretless credential provider backed by GitHub Actions OIDC."""

    def __init__(
        self,
        *,
        request_url: str,
        request_token: str | SecretStr,
        base_url: str = _DEFAULT_BASE_URL,
        audience: str = _DEFAULT_AUDIENCE,
        timeout: float = 30.0,
        monotonic_clock: Callable[[], float] = monotonic,
        utc_now: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._state = _CredentialState(
            base_url=base_url,
            request_url=request_url,
            request_token=_transport.validate_token(
                request_token,
                error_message="ACTIONS_ID_TOKEN_REQUEST_TOKEN is required for GitHub Actions OIDC.",
            ),
            audience=audience,
            timeout=timeout,
            monotonic_clock=monotonic_clock,
            utc_now=utc_now,
        )
        self._lock = anyio.Lock()
        self._http = httpx2.AsyncClient(
            headers=_client_headers(),
            timeout=httpx2.Timeout(self._state.timeout),
            follow_redirects=False,
            trust_env=False,
            transport=_transport.AsyncSingleAttemptTransport(self._state.timeout),
        )

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str | None = None,
        audience: str = _DEFAULT_AUDIENCE,
        timeout: float = 30.0,
        environ: Mapping[str, str] | None = None,
        monotonic_clock: Callable[[], float] = monotonic,
        utc_now: Callable[[], datetime] = _utc_now,
    ) -> Self:
        resolved_base, request_url, request_token, validated_audience, validated_timeout = (
            _require_actions_environment(
                base_url=base_url,
                audience=audience,
                timeout=timeout,
                environ=environ,
            )
        )
        return cls(
            request_url=request_url,
            request_token=request_token,
            base_url=resolved_base,
            audience=validated_audience,
            timeout=validated_timeout,
            monotonic_clock=monotonic_clock,
            utc_now=utc_now,
        )

    @property
    def base_url(self) -> str:
        return self._state.base_url

    @property
    def lease(self) -> GitHubActionsLease | None:
        return None if self._state.active is None else self._state.active.lease

    @property
    def organization_id(self) -> UUID | None:
        current = self.lease
        return None if current is None else current.organization_id

    @property
    def repository_id(self) -> UUID | None:
        current = self.lease
        return None if current is None else current.repository_id

    def secrets(self) -> tuple[SecretStr, ...]:
        return self._state.secrets()

    async def atoken(self) -> SecretStr:
        async with self._lock:
            cached = self._state.current_if_fresh()
            if cached is not None:
                return cached
            lease = await self._aexchange_locked()
            return lease.token

    async def aexchange(self) -> GitHubActionsLease:
        async with self._lock:
            return await self._aexchange_locked()

    async def _aexchange_locked(self) -> GitHubActionsLease:
        start_mono = self._state.monotonic_clock()
        oidc_jwt = await self._afetch_oidc_token()
        self._state.remember_secret(oidc_jwt)
        lease = await self._aexchange_for_lease(oidc_jwt)
        return self._state.record(lease, start_mono)

    async def _afetch_oidc_token(self) -> SecretStr:
        label = _url_without_query(self._state.request_url)
        try:
            async with self._http.stream(
                "GET",
                self._state.request_url,
                headers={"Authorization": f"Bearer {self._state.request_token.get_secret_value()}"},
            ) as response:
                await response.aread()
                return _parse_oidc_token(response, self._state.request_url)
        except _transport.ProoflineError:
            raise
        except httpx2.HTTPError as error:
            raise _transport_exception(error, label) from None

    async def _aexchange_for_lease(self, oidc_jwt: SecretStr) -> GitHubActionsLease:
        try:
            async with self._http.stream(
                "POST",
                self._state.exchange_url,
                headers={"Authorization": f"Bearer {oidc_jwt.get_secret_value()}"},
            ) as response:
                await response.aread()
                return _parse_lease_response(response, self._state.secrets())
        except _transport.ProoflineError:
            raise
        except httpx2.HTTPError as error:
            raise _transport_exception(error, self._state.exchange_url) from None

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncGitHubActionsCredentials(base_url={self._state.base_url!r})"


@dataclass(frozen=True, slots=True)
class GitHubActionsEvent:
    """Validated GitHub Actions workflow context extracted from the runner environment."""

    event_name: str
    repository: str | None = None
    sha: str | None = None
    pull_request_head_sha: str | None = None
    pull_request_number: int | None = None
    workflow_run_head_sha: str | None = None
    workflow_run_id: int | None = None
    workflow_run_attempt: int | None = None

    @property
    def commit_under_test(self) -> str | None:
        """Return the actual commit under review rather than synthetic merge refs."""
        if self.event_name == "workflow_run":
            return self.workflow_run_head_sha
        if self.event_name in {"pull_request", "pull_request_target"}:
            return self.pull_request_head_sha
        return self.sha


def _validated_sha40(value: object) -> str | None:
    if isinstance(value, str) and _SHA40_RE.fullmatch(value):
        return value.lower()
    return None


def _positive_int(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    if isinstance(value, str) and value.isascii() and value.isdigit():
        parsed = int(value)
        if parsed > 0:
            return parsed
    return None


def _read_event_payload(path: str) -> dict[str, Any]:
    if not path:
        return {}
    try:
        with open(path, "rb") as handle:
            raw = handle.read(_MAX_EVENT_BYTES + 1)
    except OSError as error:
        raise ValueError(
            f"Could not read GITHUB_EVENT_PATH: {error.strerror or 'error'}."
        ) from None
    if len(raw) > _MAX_EVENT_BYTES:
        raise ValueError("GitHub Actions event payload exceeds 10 MiB.")
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("GitHub Actions event payload is not valid UTF-8 JSON.") from None
    if not isinstance(decoded, dict):
        raise ValueError("GitHub Actions event payload must be a JSON object.")
    return decoded


def read_github_actions_event(
    environ: Mapping[str, str] | None = None,
) -> GitHubActionsEvent | None:
    """Read validated commit and run metadata when executing inside GitHub Actions."""
    env = os.environ if environ is None else environ
    if env.get("GITHUB_ACTIONS") != "true":
        return None
    event_name = env.get("GITHUB_EVENT_NAME", "").strip()
    repository = env.get("GITHUB_REPOSITORY", "").strip() or None
    payload = _read_event_payload(env.get("GITHUB_EVENT_PATH", "").strip())

    pr_number: int | None = None
    pr_head_sha: str | None = None
    pr_obj = payload.get("pull_request")
    if isinstance(pr_obj, dict):
        pr_number = _positive_int(pr_obj.get("number"))
        head_obj = pr_obj.get("head")
        if isinstance(head_obj, dict):
            pr_head_sha = _validated_sha40(head_obj.get("sha"))

    wr_head_sha: str | None = None
    wr_id: int | None = None
    wr_attempt: int | None = None
    wr_obj = payload.get("workflow_run")
    if isinstance(wr_obj, dict):
        wr_head_sha = _validated_sha40(wr_obj.get("head_sha"))
        wr_id = _positive_int(wr_obj.get("id"))
        wr_attempt = _positive_int(wr_obj.get("run_attempt"))

    return GitHubActionsEvent(
        event_name=event_name,
        repository=repository,
        sha=_validated_sha40(env.get("GITHUB_SHA")),
        pull_request_head_sha=pr_head_sha,
        pull_request_number=pr_number,
        workflow_run_head_sha=wr_head_sha,
        workflow_run_id=wr_id or _positive_int(env.get("GITHUB_RUN_ID")),
        workflow_run_attempt=wr_attempt or _positive_int(env.get("GITHUB_RUN_ATTEMPT")),
    )


def _sanitize_text(text: str) -> str:
    return "".join(
        "\ufffd"
        if (
            (ord(ch) < 32 or 0x7F <= ord(ch) <= 0x9F or ord(ch) in _BIDI_CODEPOINTS)
            and ch not in ("\n", "\t")
        )
        else ch
        for ch in text
    )


def _escape_data(text: str) -> str:
    return _sanitize_text(text).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(text: str) -> str:
    single_line = _sanitize_text(text).replace("\t", " ")
    return (
        single_line.replace("%", "%25")
        .replace("\r", "%0D")
        .replace("\n", "%0A")
        .replace(":", "%3A")
        .replace(",", "%2C")
    )


def _validated_repo_path(path: object) -> str | None:
    if not isinstance(path, str) or not path:
        return None
    if path.startswith("/") or "\\" in path:
        return None
    if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
        return None
    if any(ord(ch) < 32 or 0x7F <= ord(ch) <= 0x9F or ord(ch) in _BIDI_CODEPOINTS for ch in path):
        return None
    segments = path.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        return None
    return path


def _is_positive_line(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 1:
        return value
    return None


def _primary_location(
    refs: list[CustomerEvidenceRef],
    head_sha: str | None,
) -> tuple[str, int | None, int | None] | None:
    for ref in refs:
        if ref.kind != "repository_file":
            continue
        companion = ref.companion_repository
        if isinstance(companion, str) and companion:
            continue
        if head_sha is not None and isinstance(ref.commit_sha, str) and ref.commit_sha:
            if ref.commit_sha.lower() != head_sha:
                continue
        repo_path = _validated_repo_path(ref.repository_path)
        if repo_path is None:
            continue
        start_line = _is_positive_line(ref.start_line)
        end_line = _is_positive_line(ref.end_line)
        if start_line is None:
            return (repo_path, None, None)
        if end_line is None or end_line < start_line:
            return (repo_path, start_line, None)
        return (repo_path, start_line, end_line)
    return None


def _active_findings(review: CustomerReviewDetail) -> list[CustomerFinding]:
    items: list[CustomerFinding] = []
    if review.assessments:
        for item in review.assessments:
            for finding in item.findings:
                if (
                    finding.risk_domain != _WITHHELD_MARKER
                    and finding.lifecycle_state not in _CLOSED_LIFECYCLES
                ):
                    items.append(finding)
        return items
    if review.assessment_count == 0:
        code = _code_assessment(review)
        if code is not None:
            for finding in code.findings:
                if (
                    finding.risk_domain != _WITHHELD_MARKER
                    and finding.lifecycle_state not in _CLOSED_LIFECYCLES
                ):
                    items.append(finding)
    return items


def _annotation_level(severity: str) -> Literal["error", "warning"]:
    if severity == "WARNING":
        return "warning"
    return "error"


def _finding_priority(finding: CustomerFinding) -> int:
    if finding.severity == "WARNING":
        return 1
    return 0


def format_github_annotations(
    outcome: ReviewOutcome,
    *,
    head_commit_sha: str | None = None,
) -> str:
    """Format active findings and review gaps as injection-safe GitHub workflow annotations."""
    if not isinstance(outcome, ReviewOutcome):
        raise TypeError("format_github_annotations expects a ReviewOutcome instance.")
    normalized_head: str | None = None
    if head_commit_sha is not None:
        normalized_head = _validated_sha40(head_commit_sha)
        if normalized_head is None:
            raise ValueError("head_commit_sha must be a full 40-character hexadecimal commit SHA.")

    lines: list[str] = []
    if outcome.review is not None:
        if normalized_head is None and isinstance(outcome.review.head_commit_sha, str):
            normalized_head = _validated_sha40(outcome.review.head_commit_sha)
        findings = sorted(_active_findings(outcome.review), key=_finding_priority)
        for finding in findings:
            level = _annotation_level(finding.severity)
            location = _primary_location(finding.evidence_refs, normalized_head)
            props: list[str] = []
            if location is not None:
                path, start_line, end_line = location
                props.append(f"file={_escape_property(path)}")
                if start_line is not None:
                    props.append(f"line={start_line}")
                    if end_line is not None and end_line > start_line:
                        props.append(f"endLine={end_line}")
            domain = finding.risk_domain.strip()
            severity_label = finding.severity.strip() or "SERIOUS"
            title = (
                f"Proofline {severity_label} ({domain})"
                if domain
                else f"Proofline {severity_label}"
            )
            props.append(f"title={_escape_property(title)}")
            claim = finding.claim.strip()
            impact = finding.impact.strip()
            detail = f"{claim} - {impact}" if impact else claim
            body = f"{detail} [{finding.id}]" if detail else f"[{finding.id}]"
            lines.append(f"::{level} {','.join(props)}::{_escape_data(body)}")

    if outcome.status != "COMPLETED" or outcome.gaps:
        reasons: list[str] = []
        seen: set[str] = set()
        for gap in outcome.gaps:
            for code in gap.reason_codes:
                if code and code not in seen:
                    seen.add(code)
                    reasons.append(code)
            if gap.incompleteness_kind and gap.incompleteness_kind not in seen:
                seen.add(gap.incompleteness_kind)
                reasons.append(gap.incompleteness_kind)
            if gap.release_evidence_gap and gap.release_evidence_gap not in seen:
                seen.add(gap.release_evidence_gap)
                reasons.append(gap.release_evidence_gap)
        parts = [f"status={outcome.status}"]
        if reasons:
            parts.append(f"reasons={','.join(reasons)}")
        if outcome.reason:
            parts.append(outcome.reason)
        lines.append(
            f"::warning title={_escape_property(f'Proofline review {outcome.status}')}::"
            f"{_escape_data('; '.join(parts))} ({_escape_data(outcome.review_url)})"
        )

    return "\n".join(lines)
