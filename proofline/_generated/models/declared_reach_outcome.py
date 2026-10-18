from enum import StrEnum


class DeclaredReachOutcome(StrEnum):
    NO_ROOTS = "NO_ROOTS"
    READ = "READ"
    ROOTS_UNKNOWN = "ROOTS_UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"

    def __str__(self) -> str:
        return str(self.value)
