from enum import StrEnum


class FindingOutcomesPostMergeOutcome(StrEnum):
    ADDRESSED = "ADDRESSED"
    INCOMPLETE = "INCOMPLETE"
    NOT_ADDRESSED = "NOT_ADDRESSED"

    def __str__(self) -> str:
        return str(self.value)
