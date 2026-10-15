from enum import StrEnum


class Dataset(StrEnum):
    FINDINGS = "findings"
    FINDING_OUTCOMES = "finding_outcomes"
    FINDING_VALIDATIONS = "finding_validations"
    REVIEWS = "reviews"
    SPEND = "spend"

    def __str__(self) -> str:
        return str(self.value)
