from enum import StrEnum


class ActionUnavailability(StrEnum):
    PERMISSION_CHECK_UNAVAILABLE = "PERMISSION_CHECK_UNAVAILABLE"
    READ_ONLY = "READ_ONLY"
    REPOSITORY_UNAVAILABLE = "REPOSITORY_UNAVAILABLE"
    REPOSITORY_WRITE_REQUIRED = "REPOSITORY_WRITE_REQUIRED"

    def __str__(self) -> str:
        return str(self.value)
