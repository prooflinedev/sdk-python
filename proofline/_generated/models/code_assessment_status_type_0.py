from enum import StrEnum


class CodeAssessmentStatusType0(StrEnum):
    COMPLETED = "COMPLETED"
    INCOMPLETE = "INCOMPLETE"
    PENDING = "PENDING"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
