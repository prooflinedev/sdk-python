from enum import StrEnum


class ProviderWaitReason(StrEnum):
    GITHUB_RATE_LIMIT = "GITHUB_RATE_LIMIT"

    def __str__(self) -> str:
        return str(self.value)
