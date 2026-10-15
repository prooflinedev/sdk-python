from enum import StrEnum


class AgentVendor(StrEnum):
    CURSOR_CLOUD_AGENTS = "CURSOR_CLOUD_AGENTS"
    DEVIN = "DEVIN"

    def __str__(self) -> str:
        return str(self.value)
