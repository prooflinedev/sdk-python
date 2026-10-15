from enum import StrEnum


class PatchTriggerSource(StrEnum):
    HOOK_PRE_COMMIT = "HOOK_PRE_COMMIT"
    HOOK_PRE_PUSH = "HOOK_PRE_PUSH"

    def __str__(self) -> str:
        return str(self.value)
