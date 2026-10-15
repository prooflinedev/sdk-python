from enum import StrEnum


class ThreadProviderState(StrEnum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"

    def __str__(self) -> str:
        return str(self.value)
