from enum import StrEnum


class ExportEvidenceKind(StrEnum):
    COMMIT = "commit"
    COMPANION_REPOSITORY_FILE = "companion_repository_file"
    DETERMINISTIC_TEST = "deterministic_test"
    RECORDED_READ = "recorded_read"
    REPOSITORY_FILE = "repository_file"
    REPOSITORY_FILE_AT_COMMIT = "repository_file_at_commit"
    TEXT = "text"
    WORKFLOW_RUN = "workflow_run"
    WORLD_ENTITY = "world_entity"

    def __str__(self) -> str:
        return str(self.value)
