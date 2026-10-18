from enum import StrEnum


class ProseOutcomeType0(StrEnum):
    PUBLISHED = "PUBLISHED"

    def __str__(self) -> str:
        return str(self.value)
