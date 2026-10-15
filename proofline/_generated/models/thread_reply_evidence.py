from enum import StrEnum


class ThreadReplyEvidence(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    NONE_CONFIRMED = "NONE_CONFIRMED"
    RECORDED = "RECORDED"

    def __str__(self) -> str:
        return str(self.value)
