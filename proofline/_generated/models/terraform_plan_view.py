from enum import StrEnum


class TerraformPlanView(StrEnum):
    ADDRESSES_UNREPORTED = "ADDRESSES_UNREPORTED"
    HEAD_DIFFERS = "HEAD_DIFFERS"
    NOT_DECLARED = "NOT_DECLARED"
    NOT_PINNED = "NOT_PINNED"
    TAKEN = "TAKEN"

    def __str__(self) -> str:
        return str(self.value)
