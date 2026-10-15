from enum import StrEnum


class PermissionView(StrEnum):
    BLOCK = "BLOCK"
    PERMIT = "PERMIT"

    def __str__(self) -> str:
        return str(self.value)
