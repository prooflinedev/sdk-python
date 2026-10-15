from enum import StrEnum


class OpenItemsHeadState(StrEnum):
    CURRENT = "CURRENT"
    OUTDATED = "OUTDATED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
