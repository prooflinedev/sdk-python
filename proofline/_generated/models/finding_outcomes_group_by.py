from enum import StrEnum


class FindingOutcomesGroupBy(StrEnum):
    ENVIRONMENT = "environment"
    REPOSITORY = "repository"
    RISK_DOMAIN = "risk_domain"
    SEVERITY = "severity"
    SUBJECT_KIND = "subject_kind"

    def __str__(self) -> str:
        return str(self.value)
