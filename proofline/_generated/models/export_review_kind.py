from enum import StrEnum


class ExportReviewKind(StrEnum):
    COMMIT = "COMMIT"
    DEPLOYMENT = "DEPLOYMENT"
    PATCH = "PATCH"
    PULL_REQUEST = "PULL_REQUEST"

    def __str__(self) -> str:
        return str(self.value)
