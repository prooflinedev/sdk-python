from enum import StrEnum


class GateStatus(StrEnum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    BYPASSED = "BYPASSED"
    EVALUATING = "EVALUATING"
    REQUESTED = "REQUESTED"
    SUPERSEDED = "SUPERSEDED"

    def __str__(self) -> str:
        return str(self.value)
