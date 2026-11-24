from enum import StrEnum


class StoredCheckResultSource(StrEnum):
    REPRODUCTION = "REPRODUCTION"
    RERUN = "RERUN"

    def __str__(self) -> str:
        return str(self.value)
