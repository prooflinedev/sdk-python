from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from proofline import (
    AssessmentGap,
    CheckGap,
    ReviewOutcome,
    outcome_markdown,
    write_github_step_summary,
)

URL = "https://proofline.sh/app/org/reviews/00000000-0000-4000-8000-000000000001"
ASSESSMENT = UUID("1234abcd-0000-4000-8000-000000000002")


def _gap(*checks: CheckGap, reasons: tuple[str, ...] = ("CHECKS_UNRESOLVED",)) -> AssessmentGap:
    return AssessmentGap(ASSESSMENT, "COMPLETED", reasons, checks=checks)


def test_completed_outcome_links_the_review() -> None:
    text = outcome_markdown(ReviewOutcome("COMPLETED", URL))

    assert text.startswith("### Proofline review completed\n")
    assert f"[Open the review in Proofline]({URL})" in text
    assert "not a pass" not in text
    assert "| Assessment |" not in text


@pytest.mark.parametrize("status", ["INCOMPLETE", "FAILED", "STOPPED", "TIMED_OUT"])
def test_every_other_status_is_marked_as_not_a_pass(status: str) -> None:
    text = outcome_markdown(ReviewOutcome(status, URL))  # type: ignore[arg-type]

    assert "Do not treat this result as a pass." in text
    assert "### Proofline review completed" not in text


def test_gaps_and_unresolved_checks_are_listed() -> None:
    check = CheckGap("unit tests", "FAILING", "GATING")
    outcome = ReviewOutcome(
        "INCOMPLETE",
        URL,
        gaps=(_gap(check), AssessmentGap(None, "UNKNOWN", ("ASSESSMENT_HISTORY_UNAVAILABLE",))),
    )

    text = outcome_markdown(outcome)

    assert "| `1234abcd` | COMPLETED | CHECKS\\_UNRESOLVED |" in text
    assert "| Review | UNKNOWN | ASSESSMENT\\_HISTORY\\_UNAVAILABLE |" in text
    assert "| `1234abcd` | unit tests | FAILING | GATING |" in text


def test_free_text_detail_and_unresolved_reason_are_left_out() -> None:
    check = CheckGap(
        "deploy",
        "UNRESOLVED",
        "GATING",
        unresolved_reason="token=s3cret-reason",
        detail="DATABASE_URL=postgres://user:s3cret-detail@db",
    )

    text = outcome_markdown(ReviewOutcome("INCOMPLETE", URL, gaps=(_gap(check),)))

    assert "s3cret" not in text
    assert "deploy" in text


def test_server_text_cannot_break_the_table_or_inject_markup() -> None:
    hostile = "a | b\n<img src=x onerror=alert(1)> [link](https://evil.test) `code`"
    check = CheckGap(hostile, "FAILING", "GATING")

    text = outcome_markdown(ReviewOutcome("INCOMPLETE", URL, gaps=(_gap(check),)))
    row = next(line for line in text.splitlines() if "img" in line)

    assert row.count("|") - row.count("\\|") == 5
    assert "\\<img" in row
    assert "<" not in text.replace("\\<", "")
    assert "](https://evil.test)" not in text
    assert "\\`code\\`" in row


def test_unsafe_review_url_is_not_linked() -> None:
    text = outcome_markdown(ReviewOutcome("COMPLETED", "javascript:alert(1)"))

    assert "](" not in text
    assert "Review: javascript\\:alert\\(1\\)" in text


def test_long_gap_lists_are_capped() -> None:
    checks = tuple(CheckGap(f"check {index}", "FAILING", "GATING") for index in range(60))

    text = outcome_markdown(ReviewOutcome("INCOMPLETE", URL, gaps=(_gap(*checks),)))

    assert "check 49" in text
    assert "check 50" not in text
    assert "10 more in the review" in text


def test_writer_appends_to_the_step_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = tmp_path / "summary.md"
    summary.write_text("earlier step\n", encoding="utf-8")
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    outcome = ReviewOutcome("TIMED_OUT", URL)

    assert write_github_step_summary(outcome) is True
    assert summary.read_text(encoding="utf-8") == (
        "earlier step\n" + outcome_markdown(outcome) + "\n"
    )


def test_writer_is_a_no_op_outside_github_actions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    monkeypatch.chdir(tmp_path)

    assert write_github_step_summary(ReviewOutcome("COMPLETED", URL)) is False
    assert list(tmp_path.iterdir()) == []


def test_writer_accepts_an_explicit_path(tmp_path: Path) -> None:
    target = tmp_path / "out.md"

    assert write_github_step_summary(ReviewOutcome("FAILED", URL), target) is True
    assert target.read_text(encoding="utf-8").startswith("### Proofline review failed")
