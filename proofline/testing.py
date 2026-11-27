from __future__ import annotations

import json
import threading
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from string import hexdigits
from types import TracebackType
from typing import Any, Self
from urllib.parse import parse_qs, unquote, urlsplit
from uuid import UUID, uuid4

from ._generated.models.customer_finding import CustomerFinding
from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.rerun_response import RerunResponse
from ._generated.models.review_page import ReviewPage
from ._generated.models.run_now_response import RunNowResponse
from ._generated.models.stop_response import StopResponse

__all__ = [
    "DEFAULT_ORGANIZATION_ID",
    "DEFAULT_REPOSITORY_ID",
    "DEFAULT_TOKEN",
    "REVIEW_STATES",
    "FakeProofline",
    "FakeRequest",
    "FakeResponse",
    "fake_finding",
]

DEFAULT_TOKEN = "pln_test_fake_proofline_token"
DEFAULT_ORGANIZATION_ID = UUID("00000000-0000-4000-8000-00000000f001")
DEFAULT_REPOSITORY_ID = UUID("00000000-0000-4000-8000-00000000f002")
REVIEW_STATES = frozenset(("PENDING", "RUNNING", "COMPLETED", "INCOMPLETE", "FAILED", "STOPPED"))
_ACTIVE_STATES = frozenset(("PENDING", "RUNNING"))
_ENVIRONMENT = "Fake environment"
_STOPPED_BY = {"github_user_id": 1, "login": "fake-proofline"}
_API = ("api", "v1", "organizations")


@dataclass(frozen=True)
class FakeRequest:
    method: str
    path: str
    query: dict[str, list[str]]
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body) if self.body else None


@dataclass(frozen=True)
class FakeResponse:
    status: int = 200
    body: Any = None
    headers: Mapping[str, str] = field(default_factory=dict)


Handler = Callable[[FakeRequest], FakeResponse]


@dataclass
class _Failure:
    response: FakeResponse
    method: str | None
    path: str | None
    remaining: int


@dataclass
class _Review:
    id: UUID
    assessment_id: UUID
    pull_request: int
    run_number: int
    states: tuple[str, ...]
    findings: tuple[dict[str, Any], ...]
    head_commit_sha: str | None
    trigger_origin: str
    created_at: str
    position: int = 0
    shown: str = ""
    requested: bool = False
    stopped: bool = False

    def current(self) -> str:
        return "STOPPED" if self.stopped else self.states[self.position]

    def read(self) -> str:
        status = self.current()
        self.position = min(self.position + 1, len(self.states) - 1)
        self.shown = status
        return status

    def listed(self) -> str:
        return "STOPPED" if self.stopped else self.shown or self.states[0]


def fake_finding(
    *,
    severity: str = "SERIOUS",
    claim: str = "A fake finding.",
    impact: str = "A fake impact.",
    risk_domain: str = "CORRECTNESS",
    finding_id: UUID | None = None,
    **fields: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": str(finding_id or uuid4()),
        "severity": severity,
        "risk_domain": risk_domain,
        "claim": claim,
        "impact": impact,
        "symbols": [],
        "lifecycle_state": "NEW",
        "evidence_refs": [],
        "rule_refs": [],
        "comment_reactions": [],
        **fields,
    }
    return _checked_finding(payload)


def _checked_finding(payload: Mapping[str, Any]) -> dict[str, Any]:
    try:
        return CustomerFinding.from_dict(dict(payload)).to_dict()
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"The finding does not match the public contract: {error!r}") from None


def _problem(status: int, title: str | None = None, detail: str | None = None) -> FakeResponse:
    try:
        phrase = HTTPStatus(status).phrase
    except ValueError:
        phrase = "Error"
    return FakeResponse(
        status,
        {
            "type": "about:blank",
            "title": title or phrase,
            "status": status,
            "detail": detail or f"The fake Proofline server answered {status} {phrase}.",
        },
        {"Content-Type": "application/problem+json"},
    )


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _matches(rule_method: str | None, rule_path: str | None, request: FakeRequest) -> bool:
    return (rule_method is None or rule_method.upper() == request.method) and (
        rule_path is None or request.path == rule_path or request.path.endswith(rule_path)
    )


class FakeProofline:
    def __init__(
        self,
        *,
        token: str = DEFAULT_TOKEN,
        organization_id: UUID = DEFAULT_ORGANIZATION_ID,
        repository_id: UUID = DEFAULT_REPOSITORY_ID,
        repository: str = "acme/api",
    ) -> None:
        if not token or any(character.isspace() for character in token):
            raise ValueError("The fake token must be a non-empty string without whitespace.")
        if repository.count("/") != 1 or not all(repository.split("/")):
            raise ValueError("The repository must be written as owner/name.")
        self.token = token
        self.organization_id = organization_id
        self.repository_id = repository_id
        self.repository = repository
        self._lock = threading.RLock()
        self._requests: list[FakeRequest] = []
        self._reviews: dict[UUID, _Review] = {}
        self._failures: list[_Failure] = []
        self._routes: list[tuple[str, str, Handler]] = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self._server.daemon_threads = True
        self._thread = threading.Thread(
            target=self._server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
        )
        self.url = f"http://127.0.0.1:{self._server.server_port}"
        self._started = False

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def start(self) -> None:
        if not self._started:
            self._started = True
            self._thread.start()

    def close(self) -> None:
        if self._started:
            self._started = False
            self._server.shutdown()
            self._thread.join(timeout=5)
        self._server.server_close()

    @property
    def requests(self) -> list[FakeRequest]:
        with self._lock:
            return list(self._requests)

    def add_review(
        self,
        *,
        pull_request: int = 1,
        states: Sequence[str] = ("COMPLETED",),
        findings: Iterable[Mapping[str, Any]] = (),
        head_commit_sha: str | None = None,
        review_id: UUID | None = None,
    ) -> UUID:
        if isinstance(pull_request, bool) or not isinstance(pull_request, int) or pull_request < 1:
            raise ValueError("The pull request number must be a positive integer.")
        if isinstance(states, str) or not states:
            raise ValueError("Give at least one review state, as a sequence of state names.")
        unknown = [state for state in states if state not in REVIEW_STATES]
        if unknown:
            raise ValueError(f"Unknown review states {unknown}; use {sorted(REVIEW_STATES)}.")
        if head_commit_sha is not None and (
            len(head_commit_sha) not in (40, 64)
            or any(character not in hexdigits for character in head_commit_sha)
        ):
            raise ValueError("The head commit must be a full 40 or 64 character hexadecimal SHA.")
        checked = tuple(_checked_finding(finding) for finding in findings)
        with self._lock:
            identifier = review_id or uuid4()
            if identifier in self._reviews:
                raise ValueError(f"A review with id {identifier} already exists.")
            review = _Review(
                identifier,
                uuid4(),
                pull_request,
                self._next_run(pull_request),
                tuple(states),
                checked,
                head_commit_sha,
                "MANUAL",
                _now(),
            )
            for state in dict.fromkeys(review.states):
                self._detail(review, state)
            self._reviews[identifier] = review
        return identifier

    def fail_next(
        self,
        status: int,
        *,
        method: str | None = None,
        path: str | None = None,
        title: str | None = None,
        detail: str | None = None,
        retry_after: str | None = None,
        times: int = 1,
    ) -> None:
        if not 400 <= status <= 599:
            raise ValueError("A failure status must be an HTTP 4xx or 5xx code.")
        if isinstance(times, bool) or not isinstance(times, int) or times < 1:
            raise ValueError("times must be a positive integer.")
        response = _problem(status, title, detail)
        if retry_after is not None:
            response = FakeResponse(
                status, response.body, {**response.headers, "Retry-After": retry_after}
            )
        with self._lock:
            self._failures.append(_Failure(response, method, path, times))

    def route(self, method: str, path: str, handler: Handler) -> None:
        with self._lock:
            self._routes.append((method.upper(), path, handler))

    def _next_run(self, pull_request: int) -> int:
        runs = [
            review.run_number
            for review in self._reviews.values()
            if review.pull_request == pull_request
        ]
        return max(runs, default=0) + 1

    def _summary(self, review: _Review, status: str) -> dict[str, Any]:
        owner_name = self.repository.split("/")[1]
        payload: dict[str, Any] = {
            "id": str(review.id),
            "public_key": f"rev_{review.id.hex}",
            "kind": "PULL_REQUEST",
            "status": status,
            "assessment_count": 1,
            "environment_display_names": [_ENVIRONMENT],
            "finding_count": len(review.findings),
            "trigger_origin": review.trigger_origin,
            "publication": "WITHHELD",
            "created_at": review.created_at,
            "repository_id": str(self.repository_id),
            "repository_name": owner_name,
            "repository_full_name": self.repository,
            "pull_request_number": review.pull_request,
            "run_number": review.run_number,
        }
        if review.head_commit_sha is not None:
            payload["head_commit_sha"] = review.head_commit_sha
        return payload

    def _detail(self, review: _Review, status: str) -> dict[str, Any]:
        active = status in _ACTIVE_STATES
        payload = {
            **self._summary(review, status),
            "assessments": [
                {
                    "id": str(review.assessment_id),
                    "environment_display_name": _ENVIRONMENT,
                    "status": status,
                    "domains": [],
                    "findings": [dict(finding) for finding in review.findings],
                    "checks": {"families": [], "receipt_recorded": True, "status": "READY"},
                }
            ],
            "stoppable": active,
            "related_reviews": [],
            "subjects": [],
            "actions": {
                "promote_findings": False,
                "publish": False,
                "rerun": not active,
                "stop": active,
                "validate_findings": False,
            },
        }
        return CustomerReviewDetail.from_dict(payload).to_dict()

    def _page(self, reviews: list[_Review], request: FakeRequest) -> FakeResponse:
        status = request.query.get("status", [None])[0]
        if status is not None:
            reviews = [review for review in reviews if review.listed() == status]
        try:
            limit = int(request.query.get("limit", ["50"])[0])
            cursor = request.query.get("cursor", [None])[0]
            start = int(cursor.removeprefix("fake:")) if cursor else 0
        except ValueError:
            return _problem(400, detail="The fake server could not read limit or cursor.")
        if not 1 <= limit <= 100 or start < 0 or (cursor and not cursor.startswith("fake:")):
            return _problem(400, detail="The fake server got an out of range limit or cursor.")
        ordered = reviews[::-1]
        chunk = ordered[start : start + limit]
        truncated = start + limit < len(ordered)
        payload = {
            "items": [self._summary(review, review.listed()) for review in chunk],
            "filters": {"repositories": [], "environments": [], "authors": []},
            "truncated": truncated,
            "next_cursor": f"fake:{start + limit}" if truncated else None,
        }
        return FakeResponse(200, ReviewPage.from_dict(payload).to_dict())

    def _review(self, identifier: str) -> _Review | None:
        try:
            return self._reviews.get(UUID(identifier))
        except ValueError:
            return None

    def _repository(self, value: str) -> bool:
        return value in (self.repository, self.repository.split("/")[1])

    def _respond(self, request: FakeRequest) -> FakeResponse:
        for failure in self._failures:
            if failure.remaining and _matches(failure.method, failure.path, request):
                failure.remaining -= 1
                return failure.response
        if request.headers.get("authorization") != f"Bearer {self.token}":
            return _problem(401, detail="The fake server expects its own bearer token.")
        for method, path, handler in self._routes:
            if _matches(method, path, request):
                return handler(request)
        segments = [unquote(part) for part in request.path.strip("/").split("/")]
        if tuple(segments[:3]) != _API or len(segments) < 5:
            return _problem(404)
        if segments[3] != str(self.organization_id):
            return _problem(404, detail="The fake server knows no such organization.")
        return self._operation(request, segments[4:])

    def _operation(self, request: FakeRequest, route: list[str]) -> FakeResponse:
        method = request.method
        if method == "GET" and route == ["reviews"]:
            return self._page(list(self._reviews.values()), request)
        if method == "GET" and len(route) == 4 and route[:2] == ["reviews", "pr"]:
            if not self._repository(route[2]) or not route[3].isdigit():
                return _problem(404)
            number = int(route[3])
            reviews = [review for review in self._reviews.values() if review.pull_request == number]
            return self._page(reviews, request)
        if method == "GET" and len(route) == 6 and route[:2] == ["reviews", "pr"]:
            if not self._repository(route[2]) or route[4] != "runs":
                return _problem(404)
            for run in self._reviews.values():
                if str(run.pull_request) == route[3] and str(run.run_number) == route[5]:
                    return FakeResponse(200, self._detail(run, run.read()))
            return _problem(404, detail="The fake server knows no such pull request run.")
        if len(route) >= 2 and route[0] == "reviews":
            review = self._review(route[1])
            if review is None:
                return _problem(404, detail="The fake server knows no such review.")
            if method == "GET" and len(route) == 2:
                return FakeResponse(200, self._detail(review, review.read()))
            if method == "POST" and route[2:] == ["stop"]:
                return self._stop(review)
            if method == "POST" and route[2:] == ["rerun"]:
                return self._rerun(review)
        if (
            method == "POST"
            and len(route) == 5
            and route[0] == "repositories"
            and route[2:5:2] == ["pull-requests", "review"]
        ):
            if route[1] != str(self.repository_id) or not route[3].isdigit():
                return _problem(404, detail="The fake server knows no such repository.")
            return self._request_review(int(route[3]))
        return _problem(404)

    def _request_review(self, pull_request: int) -> FakeResponse:
        waiting = [
            review
            for review in self._reviews.values()
            if review.pull_request == pull_request and not review.requested
        ]
        if waiting:
            review = min(waiting, key=lambda item: item.run_number)
        else:
            identifier = uuid4()
            review = _Review(
                identifier,
                uuid4(),
                pull_request,
                self._next_run(pull_request),
                ("COMPLETED",),
                (),
                None,
                "MANUAL",
                _now(),
            )
            self._reviews[identifier] = review
        review.requested = True
        payload = {
            "review_id": str(review.id),
            "run_number": review.run_number,
            "existing": False,
            "automatic_reviews_paused": False,
        }
        return FakeResponse(200, RunNowResponse.from_dict(payload).to_dict())

    def _stop(self, review: _Review) -> FakeResponse:
        if review.current() not in _ACTIVE_STATES:
            return _problem(
                409, detail="The fake server can only stop a pending or running review."
            )
        review.stopped = True
        payload = {
            "review_id": str(review.id),
            "status": "STOPPED",
            "stopped_by": dict(_STOPPED_BY),
            "stopped_at": _now(),
        }
        return FakeResponse(200, StopResponse.from_dict(payload).to_dict())

    def _rerun(self, review: _Review) -> FakeResponse:
        if review.current() in _ACTIVE_STATES:
            return _problem(409, detail="The fake server cannot rerun an unfinished review.")
        identifier = uuid4()
        rerun = _Review(
            identifier,
            uuid4(),
            review.pull_request,
            self._next_run(review.pull_request),
            review.states,
            review.findings,
            review.head_commit_sha,
            "RERUN",
            _now(),
            requested=True,
        )
        self._reviews[identifier] = rerun
        payload = {
            "review_id": str(identifier),
            "public_key": f"rev_{identifier.hex}",
            "pull_request_number": rerun.pull_request,
            "repository_name": self.repository.split("/")[1],
            "run_number": rerun.run_number,
        }
        return FakeResponse(200, RerunResponse.from_dict(payload).to_dict())

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: object) -> None:
                return None

            def do_GET(self) -> None:
                self._dispatch()

            def do_POST(self) -> None:
                self._dispatch()

            def _dispatch(self) -> None:
                parts = urlsplit(self.path)
                length = int(self.headers.get("Content-Length") or 0)
                request = FakeRequest(
                    self.command,
                    parts.path,
                    parse_qs(parts.query),
                    {key.lower(): value for key, value in self.headers.items()},
                    self.rfile.read(length) if length else b"",
                )
                with owner._lock:
                    owner._requests.append(request)
                    try:
                        response = owner._respond(request)
                    except Exception as error:
                        response = _problem(500, detail=f"The fake server failed: {error!r}")
                body = response.body
                payload = body if isinstance(body, bytes) else json.dumps(body).encode()
                self.send_response(response.status)
                headers = {"Content-Type": "application/json", **response.headers}
                for key, value in headers.items():
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return Handler
