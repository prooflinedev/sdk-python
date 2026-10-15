from enum import StrEnum


class FindingEvidenceClassType0(StrEnum):
    ANALYZER_BACKED = "ANALYZER_BACKED"
    CODE_ONLY = "CODE_ONLY"

    def __str__(self) -> str:
        return str(self.value)
