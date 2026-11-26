from types import SimpleNamespace
from typing import cast

import pytest

from proofline import AssessmentGap, ReviewOutcome, format_review_outcome
from proofline.outcomes import OutcomeStatus


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (
            ReviewOutcome(
                "COMPLETED",
                "https://example.invalid/reviews/1",
                review=SimpleNamespace(
                    kind="PULL_REQUEST",
                    head_commit_sha="a" * 40,
                    head_commit_url="https://github.example/commit/a",
                ),
            ),
            "proofline_review status=COMPLETED reviewed_commit="
            + "a" * 40
            + " pinned_revision=unknown reason_codes=unknown",
        ),
        (
            ReviewOutcome(
                "INCOMPLETE",
                "https://example.invalid/reviews/1",
                review=SimpleNamespace(
                    kind="PULL_REQUEST",
                    head_commit_sha="b" * 40,
                    head_commit_url="https://github.example/commit/b",
                ),
                gaps=(AssessmentGap(None, "UNKNOWN", ("HEAD_COMMIT_MISMATCH",)),),
            ),
            "proofline_review status=INCOMPLETE reviewed_commit="
            + "b" * 40
            + " pinned_revision=unknown reason_codes=HEAD_COMMIT_MISMATCH",
        ),
        (
            ReviewOutcome(
                "INCOMPLETE",
                "https://example.invalid/reviews/1",
                review=SimpleNamespace(
                    kind="PULL_REQUEST", head_commit_sha=None, head_commit_url=None
                ),
                gaps=(AssessmentGap(None, "UNKNOWN", ("HEAD_COMMIT_UNAVAILABLE",)),),
            ),
            "proofline_review status=INCOMPLETE reviewed_commit=unknown pinned_revision=unknown "
            "reason_codes=HEAD_COMMIT_UNAVAILABLE",
        ),
        (
            ReviewOutcome("TIMED_OUT", "https://example.invalid/reviews/1"),
            "proofline_review status=TIMED_OUT reviewed_commit=unknown pinned_revision=unknown "
            "reason_codes=unknown",
        ),
    ],
)
def test_format_review_outcome_reports_operator_facts(
    outcome: ReviewOutcome, expected: str
) -> None:
    assert format_review_outcome(outcome) == expected


@pytest.mark.parametrize("status", ("COMPLETED", "INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"))
def test_format_review_outcome_keeps_recognized_statuses(status: str) -> None:
    outcome = ReviewOutcome(cast(OutcomeStatus, status), "https://example.invalid/reviews/1")

    assert format_review_outcome(outcome).startswith(f"proofline_review status={status} ")


def test_format_review_outcome_replaces_an_unsupported_status_without_mutating_it() -> None:
    outcome = ReviewOutcome(
        cast(OutcomeStatus, "FORGED\nSTATUS"), "https://example.invalid/reviews/1"
    )

    rendered = format_review_outcome(outcome)

    assert rendered.startswith("proofline_review status=unknown ")
    assert "\n" not in rendered
    assert outcome.status == "FORGED\nSTATUS"


def test_format_review_outcome_does_not_disclose_untrusted_values() -> None:
    outcome = ReviewOutcome(
        "INCOMPLETE",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PULL_REQUEST",
            head_commit_sha="requested-sha-should-not-appear",
            head_commit_url="https://github.example/commit/not-a-sha",
        ),
        gaps=(AssessmentGap(None, "UNKNOWN", ("<server prose>",)),),
    )

    assert format_review_outcome(outcome) == (
        "proofline_review status=INCOMPLETE reviewed_commit=unknown pinned_revision=unknown "
        "reason_codes=unknown"
    )


@pytest.mark.parametrize(
    "head_commit_url",
    (
        "not-a-url",
        "https://github.example/commit/a\nFORGED",
    ),
)
def test_format_review_outcome_requires_a_safe_recorded_commit_url(
    head_commit_url: str,
) -> None:
    outcome = ReviewOutcome(
        "COMPLETED",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PULL_REQUEST",
            head_commit_sha="a" * 40,
            head_commit_url=head_commit_url,
        ),
    )

    assert format_review_outcome(outcome) == (
        "proofline_review status=COMPLETED reviewed_commit=unknown pinned_revision=unknown "
        "reason_codes=unknown"
    )


def test_format_review_outcome_preserves_summary_when_commit_url_parsing_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject_url(value: str) -> None:
        raise ValueError("could not parse commit URL")

    monkeypatch.setattr("proofline.outcomes.urlsplit", reject_url)
    outcome = ReviewOutcome(
        "COMPLETED",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PULL_REQUEST",
            head_commit_sha="a" * 40,
            head_commit_url="https://github.example/commit/a",
        ),
    )

    assert format_review_outcome(outcome) == (
        "proofline_review status=COMPLETED reviewed_commit=unknown pinned_revision=unknown "
        "reason_codes=unknown"
    )


def test_format_review_outcome_reports_a_patch_revision_without_claiming_a_commit() -> None:
    outcome = ReviewOutcome(
        "INCOMPLETE",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PATCH",
            head_commit_sha="derived-revision-42",
            head_commit_url=None,
        ),
        gaps=(AssessmentGap(None, "UNKNOWN", ("HEAD_COMMIT_MISMATCH",)),),
    )

    assert format_review_outcome(outcome) == (
        "proofline_review status=INCOMPLETE reviewed_commit=unknown "
        "pinned_revision=derived-revision-42 reason_codes=HEAD_COMMIT_MISMATCH"
    )


def test_format_review_outcome_uses_the_recorded_commit_not_the_moving_provider_head() -> None:
    outcome = ReviewOutcome(
        "COMPLETED",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PULL_REQUEST",
            head_commit_sha="a" * 40,
            head_commit_url="https://github.example/commit/a",
            current_head_commit_sha="c" * 40,
        ),
    )

    rendered = format_review_outcome(outcome)

    assert "reviewed_commit=" + "a" * 40 in rendered
    assert "c" * 40 not in rendered


def test_format_review_outcome_keeps_multiline_values_to_one_log_record() -> None:
    outcome = ReviewOutcome(
        "INCOMPLETE",
        "https://example.invalid/reviews/1",
        review=SimpleNamespace(
            kind="PATCH",
            head_commit_sha="derived\nrevision",
            head_commit_url=None,
        ),
        gaps=(AssessmentGap(None, "UNKNOWN", ("HEAD_COMMIT_MISMATCH\nFORGED",)),),
    )
    before = outcome

    rendered = format_review_outcome(outcome)

    assert rendered == (
        "proofline_review status=INCOMPLETE reviewed_commit=unknown pinned_revision=unknown "
        "reason_codes=unknown"
    )
    assert "\n" not in rendered
    assert outcome is before


@pytest.mark.parametrize(
    ("review", "expected"),
    [
        (
            None,
            "proofline_review status=TIMED_OUT reviewed_commit=unknown pinned_revision=unknown "
            "reason_codes=unknown",
        ),
        (
            SimpleNamespace(
                kind="PULL_REQUEST",
                head_commit_sha="d" * 40,
                head_commit_url="https://github.example/commit/d",
            ),
            "proofline_review status=TIMED_OUT reviewed_commit="
            + "d" * 40
            + " pinned_revision=unknown reason_codes=unknown",
        ),
    ],
)
def test_format_review_outcome_keeps_timeout_status_with_or_without_a_retained_review(
    review: object, expected: str
) -> None:
    outcome = ReviewOutcome("TIMED_OUT", "https://example.invalid/reviews/1", review=review)

    assert format_review_outcome(outcome) == expected
    assert outcome.status == "TIMED_OUT"
