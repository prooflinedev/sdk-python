"""Authentication and response policy shared by both generated HTTP clients."""

from __future__ import annotations

import ipaddress
import math
import os
import re
from asyncio import sleep as async_sleep
from collections.abc import AsyncIterator, Generator, Iterator
from contextvars import ContextVar
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import monotonic, sleep
from urllib.parse import urlsplit

import anyio
import httpx
from pydantic import SecretStr

from ._sync_http import IO_DEADLINE
from ._sync_http import Transport as SyncHTTPTransport

VERSION = "1.0.0"
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
DEADLINE: ContextVar[float | None] = ContextVar("proofline_request_deadline", default=None)


class BearerAuth(httpx.Auth):
    def __init__(self, token: SecretStr) -> None:
        self._token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers.pop("Cookie", None)
        request.headers["Authorization"] = f"Bearer {self._token.get_secret_value()}"
        yield request


class ProoflineError(Exception):
    """An RFC 9457 problem. Inspect detail explicitly; repr contains only status."""

    def __init__(self, status: int, type: str, detail: str) -> None:
        self.status = status
        self.type = type
        self.detail = detail
        super().__init__(f"Proofline request failed (HTTP {status}).")

    def __repr__(self) -> str:
        return f"ProoflineError(status={self.status})"


def token_value(token: str | SecretStr | None) -> SecretStr:
    secret = (
        token
        if isinstance(token, SecretStr)
        else SecretStr(token if token is not None else os.environ.get("PROOFLINE_TOKEN", ""))
    )
    value = secret.get_secret_value()
    if not value or any(character.isspace() for character in value):
        raise ValueError("Pass a Proofline token or set PROOFLINE_TOKEN.")
    return secret


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
        httpx.URL(value)
        parts.port
    except (ValueError, httpx.InvalidURL):
        raise ValueError("Use an HTTPS origin, or HTTP with a literal loopback address.") from None
    return value.rstrip("/")


def timeout_error() -> ProoflineError:
    return ProoflineError(0, "urn:proofline:sdk:timeout", "The request deadline expired.")


def remaining() -> float | None:
    deadline = DEADLINE.get()
    return None if deadline is None else max(0.0, deadline - monotonic())


def limit_timeout(request: httpx.Request) -> None:
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


def problem(response: httpx.Response, token: SecretStr) -> ProoflineError:
    kind = "about:blank"
    detail = "Proofline returned an HTTP error without a problem document."
    try:
        body = response.json()
        if isinstance(body, dict):
            if isinstance(body.get("type"), str):
                kind = body["type"]
            if isinstance(body.get("detail"), str):
                detail = body["detail"]
    except (ValueError, UnicodeError):
        pass
    raw = token.get_secret_value()
    return ProoflineError(
        response.status_code, kind.replace(raw, "[redacted]"), detail.replace(raw, "[redacted]")
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


def encoded_response(response: httpx.Response) -> bool:
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
        if 200 <= status < 300:
            raise timeout_error()
        raise unreadable_problem(status)


def io_deadline(deadline: float) -> float:
    caller = DEADLINE.get()
    return deadline if caller is None else min(deadline, caller)


def io_budget(deadline: float) -> float:
    budget = io_deadline(deadline) - monotonic()
    if budget <= 0:
        raise httpx.ReadTimeout("The request deadline expired.")
    return budget


class DeadlineStream(httpx.SyncByteStream):
    def __init__(self, inner: httpx.SyncByteStream, status: int, deadline: float) -> None:
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


class AsyncDeadlineStream(httpx.AsyncByteStream):
    def __init__(self, inner: httpx.AsyncByteStream, status: int, deadline: float) -> None:
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
                raise httpx.ReadTimeout("The request deadline expired.") from None
            size += len(chunk)
            check_stream(size, self._status, self._deadline)
            yield chunk
        check_stream(size, self._status, self._deadline)

    async def aclose(self) -> None:
        await self._inner.aclose()


class RetryTransport(httpx.BaseTransport):
    def __init__(self, token: SecretStr, timeout: float) -> None:
        self._token = token
        self._timeout = timeout
        self._inner = SyncHTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(4):
            limit_timeout(request)
            deadline = monotonic() + self._timeout
            marker = IO_DEADLINE.set(io_deadline(deadline))
            try:
                response = self._inner.handle_request(request)
            finally:
                IO_DEADLINE.reset(marker)
            if 300 <= response.status_code < 400:
                response.close()
                raise redirect_error(response.status_code) from None
            if encoded_response(response):
                response.close()
                raise encoding_error(response.status_code) from None
            if not isinstance(response.stream, httpx.SyncByteStream):
                response.close()
                raise unreadable_problem(response.status_code)
            response.stream = DeadlineStream(response.stream, response.status_code, deadline)
            if 200 <= response.status_code < 300:
                return response
            try:
                response.read()
                error = problem(response, self._token)
            except httpx.HTTPError:
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


class AsyncRetryTransport(httpx.AsyncBaseTransport):
    def __init__(self, token: SecretStr, timeout: float) -> None:
        self._token = token
        self._timeout = timeout
        self._inner = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(4):
            limit_timeout(request)
            deadline = monotonic() + self._timeout
            try:
                with anyio.fail_after(io_budget(deadline)):
                    response = await self._inner.handle_async_request(request)
            except TimeoutError:
                raise httpx.ReadTimeout("The request deadline expired.") from None
            if 300 <= response.status_code < 400:
                await response.aclose()
                raise redirect_error(response.status_code) from None
            if encoded_response(response):
                await response.aclose()
                raise encoding_error(response.status_code) from None
            if not isinstance(response.stream, httpx.AsyncByteStream):
                await response.aclose()
                raise unreadable_problem(response.status_code)
            response.stream = AsyncDeadlineStream(response.stream, response.status_code, deadline)
            if 200 <= response.status_code < 300:
                return response
            try:
                await response.aread()
                error = problem(response, self._token)
            except httpx.HTTPError:
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
