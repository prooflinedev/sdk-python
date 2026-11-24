"""Public retry configuration for safe, idempotent HTTP reads."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Configure retries for GET requests.

    ``max_attempts`` includes the initial request. Jitter is a fractional
    variation applied only to client-computed exponential backoff; an explicit
    server ``Retry-After`` value is never randomized.
    """

    max_attempts: int = 4
    retryable_statuses: frozenset[int] = field(default_factory=lambda: frozenset((429, 503)))
    initial_backoff: float = 1.0
    backoff_multiplier: float = 2.0
    max_backoff: float = 60.0
    jitter: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.max_attempts, bool) or not isinstance(self.max_attempts, int):
            raise ValueError("Retry max_attempts must be an integer from 1 through 10.")
        if not 1 <= self.max_attempts <= 10:
            raise ValueError("Retry max_attempts must be an integer from 1 through 10.")
        try:
            supplied_statuses = tuple(self.retryable_statuses)
        except TypeError:
            raise ValueError("Retry statuses must be a collection of HTTP error codes.") from None
        if any(
            isinstance(status, bool) or not isinstance(status, int) or not 400 <= status <= 599
            for status in supplied_statuses
        ):
            raise ValueError("Retry statuses must be HTTP error codes from 400 through 599.")
        statuses = frozenset(supplied_statuses)
        forbidden = statuses & {401, 403}
        if forbidden:
            raise ValueError("HTTP 401 and 403 cannot be configured as retryable statuses.")
        object.__setattr__(self, "retryable_statuses", statuses)

        values = {
            "initial_backoff": self.initial_backoff,
            "backoff_multiplier": self.backoff_multiplier,
            "max_backoff": self.max_backoff,
            "jitter": self.jitter,
        }
        try:
            invalid_number = any(
                isinstance(value, bool)
                or not isinstance(value, int | float)
                or not math.isfinite(value)
                for value in values.values()
            )
        except OverflowError:
            invalid_number = True
        if invalid_number:
            raise ValueError("Retry backoff and jitter values must be finite numbers.")
        if self.initial_backoff < 0:
            raise ValueError("Retry initial_backoff must be nonnegative.")
        if self.backoff_multiplier < 1:
            raise ValueError("Retry backoff_multiplier must be at least 1.")
        if self.max_backoff < self.initial_backoff:
            raise ValueError("Retry max_backoff must be at least initial_backoff.")
        if not 0 <= self.jitter <= 1:
            raise ValueError("Retry jitter must be between 0 and 1.")


DEFAULT_RETRY_POLICY = RetryPolicy()
