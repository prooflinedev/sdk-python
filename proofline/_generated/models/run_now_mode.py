from enum import StrEnum


class RunNowMode(StrEnum):
    EXISTING_OR_NEW = "EXISTING_OR_NEW"
    FULL = "FULL"

    def __str__(self) -> str:
        return str(self.value)
