from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.code_assessment_status_type_0 import CodeAssessmentStatusType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_finding import CustomerFinding


T = TypeVar("T", bound="CustomerCodeAssessment")


@_attrs_define
class CustomerCodeAssessment:
    """The review's code assessment as it recorded its run. Its findings
    rest on the pinned code alone, never on World evidence.

       Attributes:
           base_commit_sha (str): The base commit the code assessment compared the head with.
           findings (list[CustomerFinding]): The code-only findings the code assessment recorded, `SERIOUS` first.
                An empty list does not establish deployment safety.
           head_commit_sha (str): The head commit the code assessment read.
           id (UUID): The code assessment's ID.
           status (CodeAssessmentStatusType0 | Literal['EXCLUDED']): A code assessment's recorded execution status. It is
               never a verdict on
                the change: only `COMPLETED` says the assessment covered what it read.
           completed_at (datetime.datetime | None | Unset): When the code assessment ended. Null while it has not.
           incompleteness_kind (None | str | Unset): Why an `INCOMPLETE` code assessment is incomplete: `NOT_CONFIGURED`,
                `POLICY_EXCLUDED`, `EVIDENCE_UNAVAILABLE`, `HYPOTHESES_UNRESOLVED` or
                `MODEL_BUDGET_EXHAUSTED`. Null otherwise.
           started_at (datetime.datetime | None | Unset): When the code assessment started. Null until it starts.
    """

    base_commit_sha: str
    findings: list[CustomerFinding]
    head_commit_sha: str
    id: UUID
    status: CodeAssessmentStatusType0 | Literal["EXCLUDED"]
    completed_at: datetime.datetime | None | Unset = UNSET
    incompleteness_kind: None | str | Unset = UNSET
    started_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_commit_sha = self.base_commit_sha

        findings = []
        for findings_item_data in self.findings:
            findings_item = findings_item_data.to_dict()
            findings.append(findings_item)

        head_commit_sha = self.head_commit_sha

        id = str(self.id)

        status: Literal["EXCLUDED"] | str
        if isinstance(self.status, CodeAssessmentStatusType0):
            status = self.status.value
        else:
            status = self.status

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        incompleteness_kind: None | str | Unset
        if isinstance(self.incompleteness_kind, Unset):
            incompleteness_kind = UNSET
        else:
            incompleteness_kind = self.incompleteness_kind

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_commit_sha": base_commit_sha,
                "findings": findings,
                "head_commit_sha": head_commit_sha,
                "id": id,
                "status": status,
            }
        )
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if incompleteness_kind is not UNSET:
            field_dict["incompleteness_kind"] = incompleteness_kind
        if started_at is not UNSET:
            field_dict["started_at"] = started_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_finding import CustomerFinding  # noqa: PLC0415

        d = dict(src_dict)
        base_commit_sha = d.pop("base_commit_sha")

        findings = []
        _findings = d.pop("findings")
        for findings_item_data in _findings:
            findings_item = CustomerFinding.from_dict(findings_item_data)

            findings.append(findings_item)

        head_commit_sha = d.pop("head_commit_sha")

        id = UUID(d.pop("id"))

        def _parse_status(data: object) -> CodeAssessmentStatusType0 | Literal["EXCLUDED"]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_code_assessment_status_type_0 = CodeAssessmentStatusType0(data)

                return componentsschemas_code_assessment_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "EXCLUDED"):
                raise TypeError()
            componentsschemas_code_assessment_status_type_1 = cast(Literal["EXCLUDED"], data)
            if componentsschemas_code_assessment_status_type_1 != "EXCLUDED":
                raise ValueError(
                    f"/components/schemas/CodeAssessmentStatus_type_1 must match const 'EXCLUDED', got '{componentsschemas_code_assessment_status_type_1}'"
                )
            return componentsschemas_code_assessment_status_type_1

        status = _parse_status(d.pop("status"))

        def _parse_completed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = datetime.datetime.fromisoformat(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_incompleteness_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        incompleteness_kind = _parse_incompleteness_kind(d.pop("incompleteness_kind", UNSET))

        def _parse_started_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = datetime.datetime.fromisoformat(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        customer_code_assessment = cls(
            base_commit_sha=base_commit_sha,
            findings=findings,
            head_commit_sha=head_commit_sha,
            id=id,
            status=status,
            completed_at=completed_at,
            incompleteness_kind=incompleteness_kind,
            started_at=started_at,
        )

        customer_code_assessment.additional_properties = d
        return customer_code_assessment

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
