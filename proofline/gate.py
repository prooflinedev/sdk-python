"""Measure a review outcome against a severity threshold.

``gate_review`` applies the same rule as ``proofline ci review --fail-on``
in the CLI: completeness decides first, then the server's open-finding counts,
then a complete CODE assessment's own findings by lifecycle and severity.
"""

from __future__ import annotations

from typing import Literal

from ._generated.models.open_items_view import OpenItemsView
from .outcomes import ReviewOutcome, _recorded_code, text

GateResult = Literal["REACHED", "NOT_REACHED", "NOT_COMPLETE", "UNAVAILABLE"]
SeverityThreshold = Literal["WARNING", "SERIOUS"]

# Least severe first, matching ``Severity::as_str`` in the CLI's ``severity.rs``.
_SEVERITIES: tuple[str, ...] = ("WARNING", "SERIOUS")


def gate_review(
    result: ReviewOutcome,
    *,
    fail_on: SeverityThreshold,
) -> GateResult:
    """Measure ``result`` against a severity ``threshold``.

    Returns one of four verdicts that match the CLI's exit codes
    (3, 0, 2, 4 respectively):

    - ``"REACHED"``: the completed review has an open finding at or above
      the threshold.
    - ``"NOT_REACHED"``: the completed review has none.
    - ``"NOT_COMPLETE"``: the review is incomplete, failed, or stopped,
      whatever it found.
    - ``"UNAVAILABLE"``: the wait timed out, or the completed review lacks
      valid open-finding counts, so the threshold cannot be measured.

    Raises ``ValueError`` if ``fail_on`` is not ``"WARNING"`` or ``"SERIOUS"``.
    """
    if fail_on not in _SEVERITIES:
        raise ValueError("fail_on must be WARNING or SERIOUS")
    if result.status == "TIMED_OUT":
        return "UNAVAILABLE"
    if result.status != "COMPLETED":
        return "NOT_COMPLETE"
    review = result.review
    if review is None:
        return "UNAVAILABLE"
    counts = review.open_items
    if not isinstance(counts, OpenItemsView):
        return "UNAVAILABLE"
    if not _is_count(counts.open_findings) or not _is_count(counts.serious_findings):
        return "UNAVAILABLE"
    # The server counts open findings from their current decisions, so
    # dismissed findings and unexpired risk acceptances do not count.
    if fail_on == "SERIOUS":
        if counts.serious_findings > 0:
            return "REACHED"
    else:
        if counts.open_findings > 0:
            return "REACHED"
    # CODE findings have no projected decisions, so their lifecycle and
    # severity decide. A partial CODE assessment's findings are not its
    # whole result.
    code = _recorded_code(review)
    if (
        code is not None
        and code.status == "COMPLETED"
        and not text(code.incompleteness_kind)
        and any(
            finding.lifecycle_state != "RESOLVED" and _reaches(finding.severity, fail_on)
            for finding in code.findings
        )
    ):
        return "REACHED"
    return "NOT_REACHED"


def _is_count(value: object) -> bool:
    """Whether ``value`` is a non-negative integer that is not a bool."""
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _reaches(severity: object, threshold: SeverityThreshold) -> bool:
    """Whether ``severity`` is at or above ``threshold``.

    An unknown severity, which a newer server can send, is never read as
    below a threshold.
    """
    if not isinstance(severity, str):
        return True
    index = _SEVERITIES.index(severity) if severity in _SEVERITIES else -1
    return index < 0 or index >= _SEVERITIES.index(threshold)
