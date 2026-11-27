"""Authentication and response policy shared by both generated HTTP clients."""

from __future__ import annotations

import ipaddress
import math
import os
import re
from asyncio import sleep as async_sleep
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Generator, Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import monotonic, sleep
from typing import Any, Protocol, TypeAlias, cast, runtime_checkable
from urllib.parse import urlsplit

import anyio
import httpx2
from pydantic import SecretStr

from ._generated.models import (
    RefusedEnvironment,
    RunNowRefusalViewType0,
    RunNowRefusalViewType1,
    RunNowRefusalViewType2,
    RunNowRefusalViewType3,
    RunNowRefusalViewType4,
    RunNowRefusalViewType5,
    RunNowRefusalViewType6,
    RunNowRefusalViewType7,
    RunNowRefusalViewType8,
    RunNowRefusalViewType9,
    RunNowRefused,
)
from ._generated.types import Unset
from ._sync_http import IO_DEADLINE
from ._sync_http import Transport as SyncHTTPTransport

VERSION = "10.2.2"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
WEEKDAY = r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)"
FULL_WEEKDAY = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
HTTP_DATES = tuple(
    re.compile(pattern, re.IGNORECASE | re.ASCII)
    for pattern in (
        rf"{WEEKDAY}, \d{{2}} {MONTH} \d{{4}} \d{{2}}:\d{{2}}:\d{{2}} GMT",
        rf"{FULL_WEEKDAY}, \d{{2}}-{MONTH}-(\d{{2}}) \d{{2}}:\d{{2}}:\d{{2}} GMT",
        rf"{WEEKDAY} {MONTH} [ \d]\d \d{{2}}:\d{{2}}:\d{{2}} \d{{4}}",
    )
)
# Each variant has a literal `reason`; the other fields depend on it.
RunNowRefusal: TypeAlias = (
    RunNowRefusalViewType0
    | RunNowRefusalViewType1
    | RunNowRefusalViewType2
    | RunNowRefusalViewType3
    | RunNowRefusalViewType4
    | RunNowRefusalViewType5
    | RunNowRefusalViewType6
    | RunNowRefusalViewType7
    | RunNowRefusalViewType8
    | RunNowRefusalViewType9
)
DEADLINE: ContextVar[float | None] = ContextVar("proofline_request_deadline", default=None)


@runtime_checkable
class TokenProvider(Protocol):
    def token(self) -> SecretStr: ...
    def secrets(self) -> tuple[SecretStr, ...]: ...


@runtime_checkable
class AsyncTokenProvider(Protocol):
    async def atoken(self) -> SecretStr: ...
    def secrets(self) -> tuple[SecretStr, ...]: ...


TokenSource: TypeAlias = SecretStr | TokenProvider | AsyncTokenProvider


def secret_values(source: TokenSource | Iterable[SecretStr]) -> tuple[SecretStr, ...]:
    if isinstance(source, SecretStr):
        return (source,)
    if isinstance(source, (TokenProvider, AsyncTokenProvider)):
        return source.secrets()
    return tuple(source)


class BearerAuth(httpx2.Auth):
    def __init__(self, token: TokenSource) -> None:
        self._token = token

    def sync_auth_flow(
        self, request: httpx2.Request
    ) -> Generator[httpx2.Request, httpx2.Response, None]:
        request.headers.pop("Cookie", None)
        if isinstance(self._token, SecretStr):
            secret = self._token
        elif isinstance(self._token, TokenProvider):
            secret = self._token.token()
        else:
            raise TypeError("Sync client requires a SecretStr or sync TokenProvider.")
        request.headers["Authorization"] = f"Bearer {secret.get_secret_value()}"
        yield request

    async def async_auth_flow(
        self, request: httpx2.Request
    ) -> AsyncGenerator[httpx2.Request, httpx2.Response]:
        request.headers.pop("Cookie", None)
        if isinstance(self._token, SecretStr):
            secret = self._token
        elif isinstance(self._token, AsyncTokenProvider):
            secret = await self._token.atoken()
        else:
            raise TypeError("Async client requires a SecretStr or AsyncTokenProvider.")
        request.headers["Authorization"] = f"Bearer {secret.get_secret_value()}"
        yield request


class ProoflineError(Exception):
    """An RFC 9457 problem. Inspect detail explicitly; repr contains only status.

    title names the server's problem class. A refused review request also
    carries the typed refusal, whose reason names the setting to change, and
    the repository_name it refers to.
    """

    def __init__(
        self,
        status: int,
        type: str,
        detail: str,
        *,
        title: str | None = None,
        refusal: RunNowRefusal | None = None,
        repository_name: str | None = None,
    ) -> None:
        self.status = status
        self.type = type
        self.detail = detail
        self.title = title
        self.refusal = refusal
        self.repository_name = repository_name
        super().__init__(f"Proofline request failed (HTTP {status}).")

    def __repr__(self) -> str:
        return f"ProoflineError(status={self.status})"


def validate_token(
    token: str | SecretStr, *, error_message: str = "Pass a Proofline token or set PROOFLINE_TOKEN."
) -> SecretStr:
    secret = token if isinstance(token, SecretStr) else SecretStr(token)
    value = secret.get_secret_value()
    if not value or any(
        character.isspace() or ord(character) < 32 or ord(character) == 127 for character in value
    ):
        raise ValueError(error_message)
    return secret


def token_value(token: str | SecretStr | None) -> SecretStr:
    return validate_token(
        token if token is not None else os.environ.get("PROOFLINE_TOKEN", ""),
        error_message="Pass a Proofline token or set PROOFLINE_TOKEN.",
    )


def base_url(value: str) -> str:
    try:
        parts = urlsplit(value)
        if (
            not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.query
            or parts.fragment
            or parts.path not in ("", "/")
            or any(ord(character) <= 32 for character in value)
        ):
            raise ValueError
        try:
            loopback = ipaddress.ip_address(parts.hostname).is_loopback
        except ValueError:
            loopback = False
        if parts.scheme != "https" and not (parts.scheme == "http" and loopback):
            raise ValueError
        httpx2.URL(value)
        parts.port
    except (ValueError, httpx2.InvalidURL):
        raise ValueError("Use an HTTPS origin, or HTTP with a literal loopback address.") from None
    return value.rstrip("/")


def invalid_response() -> ProoflineError:
    return ProoflineError(
        0, "urn:proofline:sdk:invalid-response", "Proofline returned an invalid API response."
    )


def network_error(error: httpx2.HTTPError) -> ProoflineError:
    if isinstance(error, httpx2.TimeoutException):
        return timeout_error()
    return ProoflineError(
        0, "urn:proofline:sdk:transport-unavailable", "Could not reach the Proofline API."
    )


@contextmanager
def operation_errors() -> Iterator[None]:
    try:
        yield
    except ProoflineError:
        raise
    except httpx2.HTTPError as error:
        raise network_error(error) from None
    except Exception:
        raise invalid_response() from None


def timeout_error() -> ProoflineError:
    return ProoflineError(0, "urn:proofline:sdk:timeout", "The request deadline expired.")


def remaining() -> float | None:
    deadline = DEADLINE.get()
    return None if deadline is None else max(0.0, deadline - monotonic())


def limit_timeout(request: httpx2.Request) -> None:
    budget = remaining()
    if budget is None:
        return
    if budget <= 0:
        raise timeout_error()
    configured = request.extensions.get("timeout", {})
    request.extensions["timeout"] = {
        field: budget if configured.get(field) is None else min(budget, configured[field])
        for field in ("connect", "read", "write", "pool")
    }


def retry_delay(value: str | None, attempt: int) -> float | None:
    """An invalid or longer Retry-After returns the problem without an early retry."""
    if value is None:
        return float(2**attempt)
    value = value.strip()
    if value.isascii() and value.isdigit():
        try:
            delay = float(value)
        except (ValueError, OverflowError):
            return None
    else:
        if not any(pattern.fullmatch(value) for pattern in HTTP_DATES):
            return None
        try:
            date = parsedate_to_datetime(value)
            if date.tzinfo is None:
                date = date.replace(tzinfo=UTC)
            now = datetime.now(UTC)
            obsolete = HTTP_DATES[1].fullmatch(value)
            if obsolete:
                year = now.year // 100 * 100 + int(obsolete[1])
                date = date.replace(year=year)
                if date.year > now.year + 50 or (
                    date.year == now.year + 50 and date.timetuple()[1:6] > now.timetuple()[1:6]
                ):
                    date = date.replace(year=year - 100)
            if (
                value[:3].lower()
                != ("mon", "tue", "wed", "thu", "fri", "sat", "sun")[date.weekday()]
            ):
                return None
            delay = max(0.0, (date - now).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None
    return delay if math.isfinite(delay) and delay <= 60 else None


def redacted(value: object, raw: str | Iterable[str]) -> object:
    raws = (raw,) if isinstance(raw, str) else tuple(raw)
    secrets = tuple(sorted({item for item in raws if item}, key=len, reverse=True))
    if not secrets:
        return value
    if isinstance(value, str):
        for secret in secrets:
            value = value.replace(secret, "[redacted]")
        return value
    if isinstance(value, list):
        return [redacted(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: redacted(item, secrets) for key, item in value.items()}
    return value


def environment(value: object) -> bool:
    return isinstance(value, dict) and all(
        isinstance(value.get(key), str) for key in ("id", "external_key", "display_name", "status")
    )


def optional(value: object, check: Callable[[object], bool]) -> bool:
    return value is None or check(value)


def text(value: object) -> bool:
    return isinstance(value, str)


# The generated parser copies reason fields without checking their types, so
# each documented reason's fields are checked here before a refusal is typed.
REFUSAL_SHAPES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "TRIGGER_DISABLED": lambda view: True,
    "REPOSITORY_DISABLED": lambda view: True,
    "NO_LINKED_ENVIRONMENT": lambda view: True,
    "ENVIRONMENT_REVIEWS_OFF": lambda view: environment(view.get("environment")),
    "ENVIRONMENT_NOT_READY": lambda view: (
        environment(view.get("environment")) and optional(view.get("status_detail"), text)
    ),
    "ENVIRONMENT_EVIDENCE_UNAVAILABLE": lambda view: environment(view.get("environment")),
    "INVALID_DELIVERY_CONFIGURATION": lambda view: (
        text(view.get("detail")) and optional(view.get("environment"), environment)
    ),
    "PULL_REQUEST_UNKNOWN": lambda view: True,
    "AUTHOR_HAS_NO_SEAT": lambda view: True,
    "PULL_REQUEST_CLOSED": lambda view: True,
}


def problem(response: httpx2.Response, token: TokenSource | Iterable[SecretStr]) -> ProoflineError:
    try:
        body = response.json()
    except (ValueError, UnicodeError):
        body = None
    if not isinstance(body, dict):
        return ProoflineError(
            response.status_code,
            "about:blank",
            "Proofline returned an HTTP error without a problem document.",
        )
    raw_secrets = tuple(secret.get_secret_value() for secret in secret_values(token))
    body = cast(dict[str, Any], redacted(body, raw_secrets))
    kind = body["type"] if isinstance(body.get("type"), str) else "about:blank"
    title = body["title"] if isinstance(body.get("title"), str) else None
    if isinstance(body.get("detail"), str):
        detail = body["detail"]
    elif title is not None:
        # Logged internal errors omit detail; the problem itself still arrived.
        detail = f"Proofline returned the problem {title!r} without a detail."
    else:
        detail = "Proofline returned an HTTP error without a problem document."
    # The contract types a refusal only as a review request's 400. The 402 a
    # credit refusal answers is undocumented, so it stays a plain problem.
    if response.status_code != 400 or "refusal" not in body:
        return ProoflineError(response.status_code, kind, detail, title=title)
    try:
        view = body["refusal"]
        shape = isinstance(view, dict) and REFUSAL_SHAPES.get(str(view.get("reason")))
        if not shape or not shape(view):
            raise TypeError("refusal fields")
        refused = RunNowRefused.from_dict(body)
        if title is None or not isinstance(body.get("detail"), str):
            raise TypeError("problem fields")
        if not isinstance(refused.repository_name, str):
            raise TypeError("repository_name")
        # The generated optional parser keeps the raw value when a nested
        # environment does not parse, for example an id that is not a UUID.
        nested = getattr(refused.refusal, "environment", None)
        if not isinstance(nested, RefusedEnvironment | Unset | None):
            raise TypeError("environment")
    except (KeyError, TypeError, ValueError, AttributeError):
        return ProoflineError(
            response.status_code, "urn:proofline:sdk:invalid-response", detail, title=title
        )
    return ProoflineError(
        response.status_code,
        kind,
        detail,
        title=title,
        refusal=refused.refusal,
        repository_name=refused.repository_name,
    )


def delay_within_deadline(delay: float) -> float:
    budget = remaining()
    return delay if budget is None else min(delay, budget)


def redirect_error(status: int) -> ProoflineError:
    return ProoflineError(
        status,
        "urn:proofline:sdk:redirect-refused",
        "Redirects are refused; use the canonical Proofline origin.",
    )


def unreadable_problem(status: int) -> ProoflineError:
    return ProoflineError(status, "about:blank", "Proofline returned an unreadable HTTP problem.")


def encoded_response(response: httpx2.Response) -> bool:
    return response.headers.get("Content-Encoding", "identity").strip().lower() != "identity"


def encoding_error(status: int) -> ProoflineError:
    return ProoflineError(
        status,
        "urn:proofline:sdk:invalid-response",
        "Encoded responses are refused; the client requests identity encoding.",
    )


def check_stream(size: int, status: int, deadline: float) -> None:
    if size > MAX_RESPONSE_BYTES:
        raise ProoflineError(
            status, "urn:proofline:sdk:invalid-response", "The response exceeds 8 MiB."
        )
    budget = remaining()
    if monotonic() >= deadline or (budget is not None and budget <= 0):
        # Retryable statuses time out as an expired read does; other problems keep their status.
        if 200 <= status < 300 or status in (429, 503):
            raise timeout_error()
        raise unreadable_problem(status)


def io_deadline(deadline: float) -> float:
    caller = DEADLINE.get()
    return deadline if caller is None else min(deadline, caller)


def io_budget(deadline: float) -> float:
    budget = io_deadline(deadline) - monotonic()
    if budget <= 0:
        raise httpx2.ReadTimeout("The request deadline expired.")
    return budget


class DeadlineStream(httpx2.SyncByteStream):
    def __init__(self, inner: httpx2.SyncByteStream, status: int, deadline: float) -> None:
        self._inner = inner
        self._status = status
        self._deadline = deadline

    def __iter__(self) -> Iterator[bytes]:
        size = 0
        deadline = IO_DEADLINE.set(io_deadline(self._deadline))
        try:
            for chunk in self._inner:
                size += len(chunk)
                check_stream(size, self._status, self._deadline)
                yield chunk
            check_stream(size, self._status, self._deadline)
        finally:
            IO_DEADLINE.reset(deadline)

    def close(self) -> None:
        self._inner.close()


class AsyncDeadlineStream(httpx2.AsyncByteStream):
    def __init__(self, inner: httpx2.AsyncByteStream, status: int, deadline: float) -> None:
        self._inner = inner
        self._status = status
        self._deadline = deadline

    async def __aiter__(self) -> AsyncIterator[bytes]:
        size = 0
        iterator = self._inner.__aiter__()
        while True:
            try:
                with anyio.fail_after(io_budget(self._deadline)):
                    chunk = await anext(iterator)
            except StopAsyncIteration:
                break
            except TimeoutError:
                raise httpx2.ReadTimeout("The request deadline expired.") from None
            size += len(chunk)
            check_stream(size, self._status, self._deadline)
            yield chunk
        check_stream(size, self._status, self._deadline)

    async def aclose(self) -> None:
        await self._inner.aclose()


def _prepare_sync_response(response: httpx2.Response, deadline: float) -> None:
    if 300 <= response.status_code < 400:
        response.close()
        raise redirect_error(response.status_code) from None
    if encoded_response(response):
        response.close()
        raise encoding_error(response.status_code) from None
    if not isinstance(response.stream, httpx2.SyncByteStream):
        response.close()
        raise unreadable_problem(response.status_code)
    response.stream = DeadlineStream(response.stream, response.status_code, deadline)


async def _prepare_async_response(response: httpx2.Response, deadline: float) -> None:
    if 300 <= response.status_code < 400:
        await response.aclose()
        raise redirect_error(response.status_code) from None
    if encoded_response(response):
        await response.aclose()
        raise encoding_error(response.status_code) from None
    if not isinstance(response.stream, httpx2.AsyncByteStream):
        await response.aclose()
        raise unreadable_problem(response.status_code)
    response.stream = AsyncDeadlineStream(response.stream, response.status_code, deadline)


def validate_timeout(timeout: float) -> float:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("The HTTP timeout must be a finite positive number of seconds.")
    return timeout


def read_checked_sync(
    inner: httpx2.BaseTransport,
    request: httpx2.Request,
    timeout: float,
) -> httpx2.Response:
    limit_timeout(request)
    deadline = monotonic() + timeout
    marker = IO_DEADLINE.set(io_deadline(deadline))
    try:
        response = inner.handle_request(request)
    finally:
        IO_DEADLINE.reset(marker)
    _prepare_sync_response(response, deadline)
    return response


async def read_checked_async(
    inner: httpx2.AsyncBaseTransport,
    request: httpx2.Request,
    timeout: float,
) -> httpx2.Response:
    limit_timeout(request)
    deadline = monotonic() + timeout
    try:
        with anyio.fail_after(io_budget(deadline)):
            response = await inner.handle_async_request(request)
    except TimeoutError:
        raise httpx2.ReadTimeout("The request deadline expired.") from None
    await _prepare_async_response(response, deadline)
    return response


class SingleAttemptTransport(httpx2.BaseTransport):
    def __init__(self, timeout: float) -> None:
        self._timeout = validate_timeout(timeout)
        self._inner = SyncHTTPTransport()

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        return read_checked_sync(self._inner, request, self._timeout)

    def close(self) -> None:
        self._inner.close()


class AsyncSingleAttemptTransport(httpx2.AsyncBaseTransport):
    def __init__(self, timeout: float) -> None:
        self._timeout = validate_timeout(timeout)
        self._inner = httpx2.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        return await read_checked_async(self._inner, request, self._timeout)

    async def aclose(self) -> None:
        await self._inner.aclose()


class RetryTransport(httpx2.BaseTransport):
    def __init__(self, token: TokenSource, timeout: float) -> None:
        self._token = token
        self._timeout = timeout
        self._inner = SyncHTTPTransport()

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        for attempt in range(4):
            if attempt > 0 and isinstance(self._token, TokenProvider):
                request.headers["Authorization"] = (
                    f"Bearer {self._token.token().get_secret_value()}"
                )
            response = read_checked_sync(self._inner, request, self._timeout)
            if 200 <= response.status_code < 300:
                return response
            try:
                response.read()
                error = problem(response, self._token)
            except httpx2.HTTPError:
                if response.status_code in (429, 503):
                    raise
                error = unreadable_problem(response.status_code)
            finally:
                response.close()
            delay = retry_delay(response.headers.get("Retry-After"), attempt)
            if (
                request.method != "GET"
                or response.status_code not in (429, 503)
                or attempt == 3
                or delay is None
            ):
                raise error from None
            sleep(delay_within_deadline(delay))
        raise timeout_error()

    def close(self) -> None:
        self._inner.close()


class AsyncRetryTransport(httpx2.AsyncBaseTransport):
    def __init__(self, token: TokenSource, timeout: float) -> None:
        self._token = token
        self._timeout = timeout
        self._inner = httpx2.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        for attempt in range(4):
            if attempt > 0 and isinstance(self._token, AsyncTokenProvider):
                secret = await self._token.atoken()
                request.headers["Authorization"] = f"Bearer {secret.get_secret_value()}"
            response = await read_checked_async(self._inner, request, self._timeout)
            if 200 <= response.status_code < 300:
                return response
            try:
                await response.aread()
                error = problem(response, self._token)
            except httpx2.HTTPError:
                if response.status_code in (429, 503):
                    raise
                error = unreadable_problem(response.status_code)
            finally:
                await response.aclose()
            delay = retry_delay(response.headers.get("Retry-After"), attempt)
            if (
                request.method != "GET"
                or response.status_code not in (429, 503)
                or attempt == 3
                or delay is None
            ):
                raise error from None
            await async_sleep(delay_within_deadline(delay))
        raise timeout_error()

    async def aclose(self) -> None:
        await self._inner.aclose()
