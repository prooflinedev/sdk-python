"""Typed clients for the bearer-authorized Proofline review API."""

from pydantic import SecretStr

from ._generated import models
from ._generated.models import (
    AgentSession,
    AgentVendor,
    CommitReviewRequest,
    CommitReviewResponse,
    CoverageUploadRequest,
    CoverageUploadResponse,
    CustomerAssessmentDetail,
    CustomerFinding,
    CustomerReviewDetail,
    FileReviewRequest,
    FileReviewResponse,
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
    StopResponse,
    UploadedReport,
)
from ._transport import VERSION as __version__
from ._transport import ProoflineError, RunNowRefusal
from .client import AsyncProoflineClient, ProoflineClient, ReviewFilters
from .exports import ExportDataset, ExportFormat, ExportPage
from .outcomes import AssessmentGap, CheckGap, ReviewOutcome
from .sarif import SarifExportError, review_sarif

__all__ = [
    "AgentSession",
    "AgentVendor",
    "AssessmentGap",
    "AsyncProoflineClient",
    "CheckGap",
    "CommitReviewRequest",
    "CommitReviewResponse",
    "CoverageUploadRequest",
    "CoverageUploadResponse",
    "CustomerAssessmentDetail",
    "CustomerFinding",
    "CustomerReviewDetail",
    "ExportDataset",
    "ExportFormat",
    "ExportPage",
    "FileReviewRequest",
    "FileReviewResponse",
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
    "review_sarif",
    "RunNowMode",
    "RunNowRefusal",
    "RunNowRequest",
    "RunNowResponse",
    "SarifExportError",
    "SecretStr",
    "StartSession",
    "StopResponse",
    "UploadedReport",
    "__version__",
    "models",
]

from .knowledge import KnowledgeResult as KnowledgeResult
