from enum import StrEnum


class ReviewDepth(StrEnum):
    STANDARD = "STANDARD"

    def __str__(self) -> str:
        return str(self.value)
