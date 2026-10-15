from enum import StrEnum


class ExportValidation(StrEnum):
    ACCEPTED_RISK = "ACCEPTED_RISK"
    ALREADY_COVERED = "ALREADY_COVERED"
    CONFIRMED = "CONFIRMED"
    DISMISSED = "DISMISSED"
    FIXED = "FIXED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
