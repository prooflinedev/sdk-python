from enum import StrEnum


class AvailabilityType0(StrEnum):
    LEGACY = "LEGACY"
    NOT_RECORDED = "NOT_RECORDED"
    OPERATIONAL_FAILURE = "OPERATIONAL_FAILURE"
    RECORDED = "RECORDED"

    def __str__(self) -> str:
        return str(self.value)
