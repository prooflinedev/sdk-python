"""Typed clients for the bearer-authorized Proofline review API."""

from pydantic import SecretStr

from ._generated import models
from ._generated.models import (
    AgentSession,
    AgentVendor,
    CommitReviewRequest,
    CommitReviewResponse,
    CustomerAssessmentDetail,
    CustomerFinding,
    CustomerReviewDetail,
    PatchReviewRequest,
    PatchReviewResponse,
    PatchTriggerSource,
    RepositoryGuidance,
    RepositoryNames,
    RerunResponse,
    ReviewPage,
    RunNowMode,
    RunNowRequest,
    RunNowResponse,
    StartSession,
)
from ._transport import VERSION as __version__
from ._transport import ProoflineError
from .client import AsyncProoflineClient, ProoflineClient, ReviewFilters
from .outcomes import AssessmentGap, CheckGap, ReviewOutcome

__all__ = [
    "AgentSession",
    "AgentVendor",
    "AssessmentGap",
    "AsyncProoflineClient",
    "CheckGap",
    "CommitReviewRequest",
    "CommitReviewResponse",
    "CustomerAssessmentDetail",
    "CustomerFinding",
    "CustomerReviewDetail",
    "PatchReviewRequest",
    "PatchReviewResponse",
    "PatchTriggerSource",
    "ProoflineClient",
    "ProoflineError",
    "RepositoryGuidance",
    "RepositoryNames",
    "RerunResponse",
    "ReviewFilters",
    "ReviewOutcome",
    "ReviewPage",
    "RunNowMode",
    "RunNowRequest",
    "RunNowResponse",
    "SecretStr",
    "StartSession",
    "__version__",
    "models",
]
