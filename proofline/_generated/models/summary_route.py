from enum import StrEnum


class SummaryRoute(StrEnum):
    DETERMINISTIC_ONLY = "DETERMINISTIC_ONLY"
    FULL = "FULL"
    SHORT = "SHORT"

    def __str__(self) -> str:
        return str(self.value)
