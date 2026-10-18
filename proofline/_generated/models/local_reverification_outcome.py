from enum import StrEnum


class LocalReverificationOutcome(StrEnum):
    NOT_VERIFIED = "NOT_VERIFIED"
    PENDING = "PENDING"
    RESOLVED_VERIFIED = "RESOLVED_VERIFIED"
    STILL_PRESENT = "STILL_PRESENT"

    def __str__(self) -> str:
        return str(self.value)
