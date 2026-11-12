from enum import StrEnum


class ExportReviewKind(StrEnum):
    COMMIT = "COMMIT"
    DEPLOYMENT = "DEPLOYMENT"
    FILES = "FILES"
    MERGE_GROUP = "MERGE_GROUP"
    PATCH = "PATCH"
    PULL_REQUEST = "PULL_REQUEST"
    REVISION_SCAN = "REVISION_SCAN"

    def __str__(self) -> str:
        return str(self.value)
