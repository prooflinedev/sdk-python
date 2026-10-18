from enum import StrEnum


class ChangeDiagramOutcomeType0(StrEnum):
    DRAWN = "DRAWN"

    def __str__(self) -> str:
        return str(self.value)
