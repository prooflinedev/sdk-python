from enum import StrEnum


class OpenItemsThreadUnknown(StrEnum):
    GITHUB_UNAVAILABLE = "GITHUB_UNAVAILABLE"
    READ_LIMIT_EXCEEDED = "READ_LIMIT_EXCEEDED"
    RECORDED_THREAD_MISSING = "RECORDED_THREAD_MISSING"
    REPOSITORY_UNAVAILABLE = "REPOSITORY_UNAVAILABLE"
    TRUNCATED = "TRUNCATED"

    def __str__(self) -> str:
        return str(self.value)
