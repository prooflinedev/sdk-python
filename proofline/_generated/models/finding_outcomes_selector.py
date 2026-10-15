from enum import StrEnum


class FindingOutcomesSelector(StrEnum):
    CODE_CHANGED = "code_changed"
    OUTCOME = "outcome"
    POST_MERGE = "post_merge"

    def __str__(self) -> str:
        return str(self.value)
