from __future__ import annotations

import math

import pytest

from proofline import RetryPolicy


def test_retry_policy_defaults_and_normalizes_statuses() -> None:
    assert RetryPolicy() == RetryPolicy(
        max_attempts=4,
        retryable_statuses=frozenset({429, 503}),
        initial_backoff=1,
        backoff_multiplier=2,
        max_backoff=60,
        jitter=0,
    )
    policy = RetryPolicy(retryable_statuses={429, 500})  # type: ignore[arg-type]
    assert policy.retryable_statuses == frozenset({429, 500})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_attempts": 0},
        {"max_attempts": 11},
        {"max_attempts": True},
        {"retryable_statuses": frozenset({399})},
        {"retryable_statuses": frozenset({600})},
        {"retryable_statuses": [429, 429.0]},
        {"retryable_statuses": [429.0, 429]},
        {"retryable_statuses": frozenset({401})},
        {"retryable_statuses": frozenset({403})},
        {"initial_backoff": -1},
        {"initial_backoff": math.inf},
        {"max_backoff": 10**400},
        {"backoff_multiplier": 0.5},
        {"max_backoff": 0.5, "initial_backoff": 1},
        {"jitter": -0.1},
        {"jitter": 1.1},
    ],
)
def test_retry_policy_rejects_invalid_configuration(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        RetryPolicy(**kwargs)  # type: ignore[arg-type]
