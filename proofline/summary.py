"""Markdown summaries of review outcomes for CI job pages."""

from __future__ import annotations

import os
import string
from pathlib import Path

from .outcomes import ReviewOutcome

_HEADINGS = {
    "COMPLETED": "completed",
    "INCOMPLETE": "incomplete",
    "FAILED": "failed",
    "STOPPED": "stopped",
    "TIMED_OUT": "timed out",
}
_LEADS = {
    "COMPLETED": "Every assessment finished with its evidence recorded.",
    "INCOMPLETE": "The review ended without the evidence needed to call it complete.",
    "FAILED": "The review failed.",
    "STOPPED": "The review was stopped or superseded before it finished.",
    "TIMED_OUT": "The wait ended before the review finished.",
}
_NOT_A_PASS = "Do not treat this result as a pass."
_PUNCTUATION = frozenset(string.punctuation)
_MAX_CELL = 200
_MAX_ROWS = 50


def _cell(value: object) -> str:
    """Render server text as literal Markdown that cannot break a table or add HTML."""
    text = "".join(ch if ch.isprintable() else " " for ch in str(value)).strip()
    if len(text) > _MAX_CELL:
        text = text[: _MAX_CELL - 1] + "…"
    escaped = "".join(f"\\{ch}" if ch in _PUNCTUATION else ch for ch in text)
    return escaped or "—"


def _link(url: str) -> str:
    safe = url.startswith(("https://", "http://")) and not any(
        ch.isspace() or ch in "<>()[]`\\" for ch in url
    )
    return f"[Open the review in Proofline]({url})" if safe else f"Review: {_cell(url)}"


def outcome_markdown(outcome: ReviewOutcome) -> str:
    """Return a Markdown summary of a review outcome.

    The summary names the status, the review link, each assessment gap with its reason codes,
    and each unresolved check by name, outcome and lifecycle. Free-text check detail and
    unresolved reasons are left out because they can carry withheld environment values;
    open the review to read them. Every status other than ``COMPLETED`` says it is not a pass.
    """
    status = outcome.status
    heading = _HEADINGS.get(status, _cell(status))
    lines = [f"### Proofline review {heading}", ""]
    lead = _LEADS.get(status, "The review status is not recognized.")
    if status != "COMPLETED":
        lead = f"{lead} {_NOT_A_PASS}"
    lines += [lead, ""]
    if outcome.reason:
        lines += [_cell(outcome.reason), ""]
    review = outcome.review
    if review is not None and type(getattr(review, "finding_count", None)) is int:
        count = review.finding_count
        lines += [f"Findings: {count}", ""]
    lines += [_link(outcome.review_url), ""]

    if outcome.gaps:
        lines += ["| Assessment | Status | Reasons |", "| --- | --- | --- |"]
        shown = outcome.gaps[:_MAX_ROWS]
        for gap in shown:
            label = f"`{str(gap.assessment_id)[:8]}`" if gap.assessment_id else "Review"
            reasons = ", ".join(_cell(code) for code in gap.reason_codes) or "—"
            lines.append(f"| {label} | {_cell(gap.status)} | {reasons} |")
        if len(outcome.gaps) > len(shown):
            lines.append(f"| … | | {len(outcome.gaps) - len(shown)} more in the review |")
        lines.append("")

    checks = [(gap, check) for gap in outcome.gaps for check in gap.checks]
    if checks:
        lines += [
            "| Assessment | Check | Outcome | Lifecycle |",
            "| --- | --- | --- | --- |",
        ]
        for gap, check in checks[:_MAX_ROWS]:
            label = f"`{str(gap.assessment_id)[:8]}`" if gap.assessment_id else "Review"
            lines.append(
                f"| {label} | {_cell(check.name)} | {_cell(check.outcome)} "
                f"| {_cell(check.lifecycle)} |"
            )
        if len(checks) > _MAX_ROWS:
            lines.append(f"| … | {len(checks) - _MAX_ROWS} more in the review | | |")
        lines.append("")
    return "\n".join(lines)


def write_github_step_summary(
    outcome: ReviewOutcome, path: str | os.PathLike[str] | None = None
) -> bool:
    """Append the outcome summary to the GitHub Actions job summary.

    With no ``path``, the summary goes to the file named by ``GITHUB_STEP_SUMMARY``. Outside
    GitHub Actions, when that variable is unset or empty, nothing is written and the function
    returns ``False``, so the same script runs locally. Returns ``True`` after writing.
    """
    target = path if path is not None else os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return False
    with Path(target).open("a", encoding="utf-8") as file:
        file.write(outcome_markdown(outcome) + "\n")
    return True
