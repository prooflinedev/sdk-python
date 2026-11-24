from enum import StrEnum


class QuestionsUnavailableReason(StrEnum):
    FORK_PULL_REQUEST = "FORK_PULL_REQUEST"

    def __str__(self) -> str:
        return str(self.value)
