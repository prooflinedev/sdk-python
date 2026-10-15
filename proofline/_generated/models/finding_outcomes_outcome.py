from enum import StrEnum


class FindingOutcomesOutcome(StrEnum):
    ACCEPTED_RISK = "ACCEPTED_RISK"
    ALREADY_COVERED = "ALREADY_COVERED"
    CONFIRMED = "CONFIRMED"
    DISMISSED = "DISMISSED"
    FIXED = "FIXED"
    NO_RECORDED_OUTCOME = "NO_RECORDED_OUTCOME"

    def __str__(self) -> str:
        return str(self.value)
