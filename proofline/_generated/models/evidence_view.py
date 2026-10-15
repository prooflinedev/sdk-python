from enum import StrEnum


class EvidenceView(StrEnum):
    INCOMPLETE = "INCOMPLETE"
    NO_APPLICABLE_OBLIGATIONS = "NO_APPLICABLE_OBLIGATIONS"
    REQUIRED_PROPERTIES_ESTABLISHED = "REQUIRED_PROPERTIES_ESTABLISHED"

    def __str__(self) -> str:
        return str(self.value)
