from enum import StrEnum


class CiFailureAttribution(StrEnum):
    CAUSED_BY_CHANGE = "CAUSED_BY_CHANGE"
    ENVIRONMENT_STATE = "ENVIRONMENT_STATE"
    FLAKY_OR_INFRASTRUCTURE = "FLAKY_OR_INFRASTRUCTURE"
    PRE_EXISTING_ON_BASE = "PRE_EXISTING_ON_BASE"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
