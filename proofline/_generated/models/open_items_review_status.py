from enum import StrEnum


class OpenItemsReviewStatus(StrEnum):
    COMPLETED = "COMPLETED"
    EXCLUDED = "EXCLUDED"
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
