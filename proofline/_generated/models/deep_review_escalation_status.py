from enum import StrEnum


class DeepReviewEscalationStatus(StrEnum):
    ADMITTED = "ADMITTED"
    NOT_SELECTED = "NOT_SELECTED"
    REFUSED = "REFUSED"
    UNEVALUATED = "UNEVALUATED"

    def __str__(self) -> str:
        return str(self.value)
