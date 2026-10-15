from enum import StrEnum


class RuleSource(StrEnum):
    CONFIG_FILE = "CONFIG_FILE"
    CONSOLE = "CONSOLE"
    IMPLICIT = "IMPLICIT"

    def __str__(self) -> str:
        return str(self.value)
