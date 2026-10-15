from enum import StrEnum


class ExportFindingLifecycle(StrEnum):
    NEW = "NEW"
    REINTRODUCED = "REINTRODUCED"
    RESOLVED = "RESOLVED"
    UNCHANGED = "UNCHANGED"

    def __str__(self) -> str:
        return str(self.value)
