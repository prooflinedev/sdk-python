from enum import StrEnum


class CommentAddressOutcome(StrEnum):
    ADDRESSED = "ADDRESSED"
    INCOMPLETE = "INCOMPLETE"
    NOT_ADDRESSED = "NOT_ADDRESSED"

    def __str__(self) -> str:
        return str(self.value)
