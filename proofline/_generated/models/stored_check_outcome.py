from enum import StrEnum


class StoredCheckOutcome(StrEnum):
    DID_NOT_FAIL = "DID_NOT_FAIL"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"

    def __str__(self) -> str:
        return str(self.value)
