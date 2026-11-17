from copy import deepcopy
from datetime import datetime
from uuid import UUID

import pytest

from proofline import CustomerReviewDetail, compare_review_observations
from proofline._generated.models.open_finding_counts import OpenFindingCounts
from proofline._generated.models.open_items_head_state import OpenItemsHeadState
from proofline._generated.models.review_open_items import ReviewOpenItems
from proofline._generated.types import UNSET

from .fixtures import REVIEW, review


def make_review_observation(
    *,
    observed_at: str,
    serious: int,
    warning: int,
    accepted_risks: int,
) -> CustomerReviewDetail:
    """Build a review using the same shape as an API response."""
    payload = review()

    payload["open_items_observation"] = {
        "observed_at": observed_at,
        "head_state": "CURRENT",
        "latest_review_head_state": "CURRENT",
        "is_latest_review": True,
        "review_status": "COMPLETED",
        "open_findings": {
            "serious": serious,
            "warning": warning,
        },
        "accepted_risk_count": accepted_risks,
        "evaluated_scope_known": True,
        "environments": [],
        "threads": {
            "status": "KNOWN",
            "observed_at": observed_at,
            "unresolved_count": 0,
        },
        "reviewed_head_sha": "a" * 40,
        "current_head_sha": "a" * 40,
    }

    return CustomerReviewDetail.from_dict(payload)


def test_compares_ordered_observations_without_mutating_inputs() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    earlier_before = deepcopy(earlier.to_dict())
    later_before = deepcopy(later.to_dict())

    comparison = compare_review_observations(earlier, later)

    assert comparison.review_id == REVIEW
    assert comparison.serious_delta == -1
    assert comparison.warning_delta == 2
    assert comparison.accepted_risk_delta == 0
    assert comparison.earlier_observed_at == (earlier.open_items_observation.observed_at)
    assert comparison.later_observed_at == (later.open_items_observation.observed_at)
    assert comparison.earlier_head_state == "CURRENT"
    assert comparison.later_head_state == "CURRENT"
    assert earlier.to_dict() == earlier_before
    assert later.to_dict() == later_before


@pytest.mark.parametrize(
    ("earlier_count", "later_count", "expected_delta"),
    [
        (2, 2, 0),
        (2, 4, 2),
        (4, 2, -2),
    ],
)
def test_calculates_count_deltas(
    earlier_count: int,
    later_count: int,
    expected_delta: int,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=earlier_count,
        warning=earlier_count,
        accepted_risks=earlier_count,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=later_count,
        warning=later_count,
        accepted_risks=later_count,
    )

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta == expected_delta
    assert comparison.warning_delta == expected_delta
    assert comparison.accepted_risk_delta == expected_delta


@pytest.mark.parametrize("missing_value", [None, UNSET])
@pytest.mark.parametrize(
    ("missing_side", "expected_reason"),
    [
        ("earlier", "EARLIER_OBSERVATION_UNAVAILABLE"),
        ("later", "LATER_OBSERVATION_UNAVAILABLE"),
    ],
)
def test_missing_observation_returns_unavailable_deltas(
    missing_value: object,
    missing_side: str,
    expected_reason: str,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )

    if missing_side == "earlier":
        earlier.open_items_observation = missing_value
    else:
        later.open_items_observation = missing_value

    comparison = compare_review_observations(earlier, later)

    assert comparison.review_id == REVIEW
    assert comparison.serious_delta is None
    assert comparison.warning_delta is None
    assert comparison.accepted_risk_delta is None
    assert expected_reason in comparison.unknown_reasons


@pytest.mark.parametrize(
    ("timestamp", "expected_reason"),
    [
        (None, "EARLIER_TIMESTAMP_UNAVAILABLE"),
        (datetime(2026, 11, 17, 8, 0), "EARLIER_TIMESTAMP_UNAVAILABLE"),
    ],
)
def test_invalid_timestamp_returns_unavailable_deltas(
    timestamp: object,
    expected_reason: str,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = earlier.open_items_observation
    assert isinstance(observation, ReviewOpenItems)

    # Deliberately construct malformed data to test the helper's boundary.
    setattr(observation, "observed_at", timestamp)

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta is None
    assert comparison.warning_delta is None
    assert comparison.accepted_risk_delta is None
    assert expected_reason in comparison.unknown_reasons


def test_equal_timestamps_return_unavailable_deltas() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta is None
    assert comparison.warning_delta is None
    assert comparison.accepted_risk_delta is None
    assert "SAME_TIMESTAMP" in comparison.unknown_reasons


def test_reversed_timestamps_raise_value_error() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )

    with pytest.raises(ValueError, match="earlier timestamp"):
        compare_review_observations(earlier, later)


@pytest.mark.parametrize(
    ("head", "expected_reason"),
    [
        (None, "REVIEWED_HEAD_UNAVAILABLE"),
        (UNSET, "REVIEWED_HEAD_UNAVAILABLE"),
        ("not-a-sha", "REVIEWED_HEAD_UNAVAILABLE"),
        ("b" * 40, "REVIEWED_HEAD_CHANGED"),
    ],
)
def test_incompatible_reviewed_heads_return_unavailable_deltas(
    head: object,
    expected_reason: str,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = later.open_items_observation
    assert isinstance(observation, ReviewOpenItems)
    setattr(observation, "reviewed_head_sha", head)

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta is None
    assert comparison.warning_delta is None
    assert comparison.accepted_risk_delta is None
    assert expected_reason in comparison.unknown_reasons


def test_matching_reviewed_heads_are_compared_case_insensitively() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = later.open_items_observation
    assert isinstance(observation, ReviewOpenItems)
    observation.reviewed_head_sha = "A" * 40

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta == -1
    assert comparison.unknown_reasons == ()


@pytest.mark.parametrize("invalid_count", [-1, True, "3"])
def test_invalid_serious_count_only_suppresses_serious_delta(
    invalid_count: object,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = later.open_items_observation
    assert isinstance(observation, ReviewOpenItems)
    counts = observation.open_findings
    assert isinstance(counts, OpenFindingCounts)
    setattr(counts, "serious", invalid_count)

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta is None
    assert comparison.warning_delta == 2
    assert comparison.accepted_risk_delta == 0
    assert "SERIOUS_COUNT_UNAVAILABLE" in comparison.unknown_reasons


@pytest.mark.parametrize("invalid_count", [-1, True, "3"])
@pytest.mark.parametrize("side", ["earlier", "later"])
@pytest.mark.parametrize(
    ("field", "expected_reason"),
    [
        ("warning", "WARNING_COUNT_UNAVAILABLE"),
        ("accepted_risk_count", "ACCEPTED_RISK_COUNT_UNAVAILABLE"),
    ],
)
def test_invalid_other_counts_only_suppress_their_delta(
    invalid_count: object,
    side: str,
    field: str,
    expected_reason: str,
) -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )

    selected = earlier if side == "earlier" else later
    observation = selected.open_items_observation
    assert isinstance(observation, ReviewOpenItems)

    if field == "warning":
        counts = observation.open_findings
        assert isinstance(counts, OpenFindingCounts)
        setattr(counts, "warning", invalid_count)
    else:
        setattr(observation, "accepted_risk_count", invalid_count)

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta == -1
    assert comparison.warning_delta == (None if field == "warning" else 2)
    assert comparison.accepted_risk_delta == (None if field == "accepted_risk_count" else 0)
    assert expected_reason in comparison.unknown_reasons


def test_different_review_ids_raise_value_error() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    later.id = UUID("00000000-0000-4000-8000-000000000099")

    with pytest.raises(ValueError, match="same review"):
        compare_review_observations(earlier, later)


def test_malformed_observation_is_unavailable() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    # Simulate malformed data retained by the API parser.
    setattr(later, "open_items_observation", {"unexpected": "data"})

    comparison = compare_review_observations(earlier, later)

    assert comparison.serious_delta is None
    assert comparison.warning_delta is None
    assert comparison.accepted_risk_delta is None
    assert "LATER_OBSERVATION_UNAVAILABLE" in comparison.unknown_reasons


def test_unknown_scope_is_reported_without_inferring_completion() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = later.open_items_observation
    assert isinstance(observation, ReviewOpenItems)
    observation.evaluated_scope_known = False
    observation.environments = []

    comparison = compare_review_observations(earlier, later)

    assert comparison.earlier_scope_known is True
    assert comparison.later_scope_known is False


def test_unknown_head_state_is_preserved() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = later.open_items_observation
    assert isinstance(observation, ReviewOpenItems)
    observation.head_state = OpenItemsHeadState.UNKNOWN

    comparison = compare_review_observations(earlier, later)

    assert comparison.earlier_head_state == "CURRENT"
    assert comparison.later_head_state == "UNKNOWN"


def test_missing_observation_does_not_expose_malformed_other_fields() -> None:
    earlier = make_review_observation(
        observed_at="2026-11-17T08:00:00+00:00",
        serious=3,
        warning=2,
        accepted_risks=1,
    )
    later = make_review_observation(
        observed_at="2026-11-17T08:05:00+00:00",
        serious=2,
        warning=4,
        accepted_risks=1,
    )
    observation = earlier.open_items_observation
    assert isinstance(observation, ReviewOpenItems)

    setattr(observation, "observed_at", "not-a-timestamp")
    setattr(observation, "head_state", "unexpected-server-text")
    later.open_items_observation = None

    comparison = compare_review_observations(earlier, later)

    assert comparison.earlier_observed_at is None
    assert comparison.earlier_head_state is None
    assert comparison.serious_delta is None
    assert "LATER_OBSERVATION_UNAVAILABLE" in comparison.unknown_reasons
    assert "unexpected-server-text" not in repr(comparison)
