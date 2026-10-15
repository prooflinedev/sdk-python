from enum import StrEnum


class ThreadObservationFreshness(StrEnum):
    FRESH = "FRESH"
    STALE = "STALE"

    def __str__(self) -> str:
        return str(self.value)
