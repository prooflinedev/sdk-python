"""A scan request names its own resolution, so repeating it cannot scan twice."""

from __future__ import annotations

import math
import random
from uuid import UUID, uuid4

from ._generated.models.scan_request_body import ScanRequestBody
from ._transport import ProoflineError

ATTEMPTS = 4
RETRYABLE_STATUSES = frozenset((429, 502, 503, 504))
# A timed out POST may have been accepted; the repeated request_id makes retrying it safe.
RETRYABLE_TYPES = frozenset(
    ("urn:proofline:sdk:transport-unavailable", "urn:proofline:sdk:timeout")
)


def scan_body(
    budget_credits: int,
    ref: str | None,
    commit_sha: str | None,
    request_id: UUID | None,
    timeout: float,
    wait: bool,
) -> ScanRequestBody:
    """Reject a bad call before any request that could spend credits."""

    ref = ref.strip() if ref else None
    commit_sha = commit_sha.strip() if commit_sha else None
    if bool(ref) == bool(commit_sha):
        raise ValueError("Name exactly one of ref or commit_sha.")
    if type(budget_credits) is not int or budget_credits < 0:
        raise ValueError("budget_credits must be a nonnegative integer.")
    if wait and (not math.isfinite(timeout) or timeout < 0):
        raise ValueError("The review timeout must be a finite nonnegative number of seconds.")
    return ScanRequestBody(
        budget_credits=budget_credits,
        request_id=request_id or uuid4(),
        ref=ref or None,
        commit_sha=commit_sha or None,
    )


def should_retry(error: ProoflineError) -> bool:
    return error.status in RETRYABLE_STATUSES or error.type in RETRYABLE_TYPES


def backoff(attempt: int) -> float:
    return 2**attempt * random.uniform(0.5, 1)
