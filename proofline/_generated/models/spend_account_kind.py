from enum import StrEnum


class SpendAccountKind(StrEnum):
    DEPLOYMENT = "DEPLOYMENT"
    TENANT_CREDENTIAL = "TENANT_CREDENTIAL"
    UNATTRIBUTED = "UNATTRIBUTED"

    def __str__(self) -> str:
        return str(self.value)
