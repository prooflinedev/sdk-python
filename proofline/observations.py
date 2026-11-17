"""Compare recorded observations of the same review."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ._generated.models.customer_review_detail import CustomerReviewDetail
from ._generated.models.open_finding_counts import OpenFindingCounts
from ._generated.models.open_items_head_state import OpenItemsHeadState
from ._generated.models.review_open_items import ReviewOpenItems


@dataclass(frozen=True)
class ReviewObservationComparison:
    """Recorded changes between two observations of the same review."""

    review_id: UUID
    earlier_observed_at: datetime | None
    later_observed_at: datetime | None
    earlier_head_state: str | None
    later_head_state: str | None
    serious_delta: int | None
    warning_delta: int | None
    accepted_risk_delta: int | None
    unknown_reasons: tuple[str, ...] = ()
    earlier_scope_known: bool | None = None
    later_scope_known: bool | None = None


def _valid_count(value: object) -> bool:
    # bool is a subclass of int, but it is not a valid finding count.
    return type(value) is int and value >= 0


def _valid_timestamp(value: object) -> bool:
    return (
        isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None
    )


def _valid_head(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{40}", value) is not None


def _scope_known(value: object) -> bool | None:
    if isinstance(value, ReviewOpenItems) and type(value.evaluated_scope_known) is bool:
        return value.evaluated_scope_known
    return None


def _observation_time(value: object) -> datetime | None:
    if not isinstance(value, ReviewOpenItems):
        return None
    timestamp = value.observed_at
    if isinstance(timestamp, datetime) and _valid_timestamp(timestamp):
        return timestamp
    return None


def _head_state(value: object) -> str | None:
    if isinstance(value, ReviewOpenItems) and isinstance(value.head_state, OpenItemsHeadState):
        return value.head_state.value
    return None


def compare_review_observations(
    earlier: CustomerReviewDetail,
    later: CustomerReviewDetail,
) -> ReviewObservationComparison:
    """Compare two recorded observations of the same review.

    Deltas are unavailable when the observations cannot be compared.
    Inspect ``unknown_reasons`` for details. Head states describe
    Proofline's recorded view, not necessarily the live GitHub head.
    """
    if not isinstance(earlier.id, UUID) or not isinstance(later.id, UUID) or earlier.id != later.id:
        raise ValueError("Both observations must belong to the same review.")

    first = earlier.open_items_observation
    second = later.open_items_observation

    reasons: list[str] = []

    if not isinstance(first, ReviewOpenItems):
        reasons.append("EARLIER_OBSERVATION_UNAVAILABLE")
    if not isinstance(second, ReviewOpenItems):
        reasons.append("LATER_OBSERVATION_UNAVAILABLE")

    if reasons:
        return ReviewObservationComparison(
            review_id=earlier.id,
            earlier_observed_at=_observation_time(first),
            later_observed_at=_observation_time(second),
            earlier_head_state=_head_state(first),
            later_head_state=_head_state(second),
            serious_delta=None,
            warning_delta=None,
            accepted_risk_delta=None,
            unknown_reasons=tuple(reasons),
            earlier_scope_known=_scope_known(first),
            later_scope_known=_scope_known(second),
        )

    # The missing-observation branch above has already returned if either
    # value is not a ReviewOpenItems instance.
    assert isinstance(first, ReviewOpenItems)
    assert isinstance(second, ReviewOpenItems)

    first_time = first.observed_at if _valid_timestamp(first.observed_at) else None
    second_time = second.observed_at if _valid_timestamp(second.observed_at) else None

    if first_time is None:
        reasons.append("EARLIER_TIMESTAMP_UNAVAILABLE")
    if second_time is None:
        reasons.append("LATER_TIMESTAMP_UNAVAILABLE")

    if first_time is not None and second_time is not None:
        if first_time > second_time:
            raise ValueError("The earlier observation must have an earlier timestamp.")
        if first_time == second_time:
            reasons.append("SAME_TIMESTAMP")

    if reasons:
        return ReviewObservationComparison(
            review_id=earlier.id,
            earlier_observed_at=_observation_time(first),
            later_observed_at=_observation_time(second),
            earlier_head_state=_head_state(first),
            later_head_state=_head_state(second),
            serious_delta=None,
            warning_delta=None,
            accepted_risk_delta=None,
            unknown_reasons=tuple(reasons),
            earlier_scope_known=_scope_known(first),
            later_scope_known=_scope_known(second),
        )

    first_head = first.reviewed_head_sha
    second_head = second.reviewed_head_sha

    if not _valid_head(first_head) or not _valid_head(second_head):
        reasons.append("REVIEWED_HEAD_UNAVAILABLE")
    elif (
        isinstance(first_head, str)
        and isinstance(second_head, str)
        and first_head.lower() != second_head.lower()
    ):
        reasons.append("REVIEWED_HEAD_CHANGED")

    if reasons:
        return ReviewObservationComparison(
            review_id=earlier.id,
            earlier_observed_at=_observation_time(first),
            later_observed_at=_observation_time(second),
            earlier_head_state=_head_state(first),
            later_head_state=_head_state(second),
            serious_delta=None,
            warning_delta=None,
            accepted_risk_delta=None,
            unknown_reasons=tuple(reasons),
            earlier_scope_known=_scope_known(first),
            later_scope_known=_scope_known(second),
        )

    first_counts = first.open_findings
    second_counts = second.open_findings

    def count_delta(
        earlier_value: object,
        later_value: object,
        reason: str,
    ) -> int | None:
        if not _valid_count(earlier_value) or not _valid_count(later_value):
            reasons.append(reason)
            return None

        # _valid_count has checked these values at runtime.
        assert isinstance(earlier_value, int)
        assert isinstance(later_value, int)
        return later_value - earlier_value

    if isinstance(first_counts, OpenFindingCounts):
        first_serious = first_counts.serious
        first_warning = first_counts.warning
    else:
        first_serious = None
        first_warning = None

    if isinstance(second_counts, OpenFindingCounts):
        second_serious = second_counts.serious
        second_warning = second_counts.warning
    else:
        second_serious = None
        second_warning = None

    serious_delta = count_delta(
        first_serious,
        second_serious,
        "SERIOUS_COUNT_UNAVAILABLE",
    )
    warning_delta = count_delta(
        first_warning,
        second_warning,
        "WARNING_COUNT_UNAVAILABLE",
    )
    accepted_risk_delta = count_delta(
        first.accepted_risk_count,
        second.accepted_risk_count,
        "ACCEPTED_RISK_COUNT_UNAVAILABLE",
    )

    return ReviewObservationComparison(
        review_id=earlier.id,
        earlier_observed_at=_observation_time(first),
        later_observed_at=_observation_time(second),
        earlier_head_state=_head_state(first),
        later_head_state=_head_state(second),
        serious_delta=serious_delta,
        warning_delta=warning_delta,
        accepted_risk_delta=accepted_risk_delta,
        unknown_reasons=tuple(reasons),
        earlier_scope_known=_scope_known(first),
        later_scope_known=_scope_known(second),
    )
