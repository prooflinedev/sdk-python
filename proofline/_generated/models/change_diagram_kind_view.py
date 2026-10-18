from enum import StrEnum


class ChangeDiagramKindView(StrEnum):
    FLOWCHART = "FLOWCHART"
    SEQUENCE = "SEQUENCE"

    def __str__(self) -> str:
        return str(self.value)
