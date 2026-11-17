from enum import StrEnum


class IncompleteCauseType0(StrEnum):
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    HYPOTHESES_UNRESOLVED = "HYPOTHESES_UNRESOLVED"
    MODEL_BUDGET_EXHAUSTED = "MODEL_BUDGET_EXHAUSTED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    POLICY_EXCLUDED = "POLICY_EXCLUDED"

    def __str__(self) -> str:
        return str(self.value)
