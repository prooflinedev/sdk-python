from enum import StrEnum


class ExportValidationSource(StrEnum):
    GITHUB_COMMENT = "github_comment"
    PROOFLINE = "proofline"
    UI = "ui"

    def __str__(self) -> str:
        return str(self.value)
