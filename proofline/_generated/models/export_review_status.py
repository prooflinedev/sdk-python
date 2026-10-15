from enum import StrEnum


class ExportReviewStatus(StrEnum):
    COMPLETED = "COMPLETED"
    EXCLUDED = "EXCLUDED"
    FAILED = "FAILED"
    INCOMPLETE = "INCOMPLETE"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    SUPERSEDED = "SUPERSEDED"

    def __str__(self) -> str:
        return str(self.value)
