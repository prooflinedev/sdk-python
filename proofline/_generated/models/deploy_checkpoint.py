from enum import StrEnum


class DeployCheckpoint(StrEnum):
    DAY_1 = "DAY_1"
    HOUR_1 = "HOUR_1"
    LANDING = "LANDING"
    MINUTES_20 = "MINUTES_20"

    def __str__(self) -> str:
        return str(self.value)
