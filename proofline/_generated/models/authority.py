from enum import StrEnum


class Authority(StrEnum):
    ADVISORY = "ADVISORY"
    DEPLOYMENT_POLICY = "DEPLOYMENT_POLICY"

    def __str__(self) -> str:
        return str(self.value)
