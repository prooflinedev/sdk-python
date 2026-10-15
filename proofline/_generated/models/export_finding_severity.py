from enum import StrEnum


class ExportFindingSeverity(StrEnum):
    SERIOUS = "SERIOUS"
    WARNING = "WARNING"

    def __str__(self) -> str:
        return str(self.value)
