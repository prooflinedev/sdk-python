from enum import StrEnum


class Outcome(StrEnum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"

    def __str__(self) -> str:
        return str(self.value)
