from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.export_finding_lifecycle import ExportFindingLifecycle
from ..models.export_finding_severity import ExportFindingSeverity
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.export_evidence_ref import ExportEvidenceRef


T = TypeVar("T", bound="FindingsExportRow")


@_attrs_define
class FindingsExportRow:
    """One immutable finding occurrence. Reference payloads and evidence values stay private.

    Attributes:
        assessment_id (UUID): The environment or code assessment that recorded the finding; `lane` says which.
        claim (str): The finding's claim, with supported credential shapes masked as `<REDACTED:kind>`.
        created_at (datetime.datetime): When the finding was recorded; the export window filters on this time.
        dataset_version (int): The row contract version, always `2`.
        evidence_refs (list[ExportEvidenceRef]): The finding's evidence references in recorded order, each reduced to a
            kind and an
             opaque ID; an empty list means the finding records none.
        finding_id (UUID): The stable ID of this finding occurrence.
        impact (str): The finding's stated impact, with supported credential shapes masked.
        lane (Literal['CODE'] | Literal['ENVIRONMENT']): The review lane whose assessment recorded a finding.
        lifecycle_state (ExportFindingLifecycle):
        organization_id (UUID): The organization that owns the finding.
        review_id (UUID): The review whose assessment recorded the finding.
        risk_domain (str): The risk domain the finding is recorded under.
        severity (ExportFindingSeverity):
        environment_id (None | Unset | UUID): The environment the assessment covers, null for a code-lane finding.
        remediation (None | str | Unset): The suggested remediation with credential shapes masked, null when none is
            recorded.
        repository_id (None | Unset | UUID): The review's primary repository, null when the review records none.
        series_id (None | Unset | UUID): The finding series this occurrence belongs to, null when it belongs to none.
    """

    assessment_id: UUID
    claim: str
    created_at: datetime.datetime
    dataset_version: int
    evidence_refs: list[ExportEvidenceRef]
    finding_id: UUID
    impact: str
    lane: Literal["CODE"] | Literal["ENVIRONMENT"]
    lifecycle_state: ExportFindingLifecycle
    organization_id: UUID
    review_id: UUID
    risk_domain: str
    severity: ExportFindingSeverity
    environment_id: None | Unset | UUID = UNSET
    remediation: None | str | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    series_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_id = str(self.assessment_id)

        claim = self.claim

        created_at = self.created_at.isoformat()

        dataset_version = self.dataset_version

        evidence_refs = []
        for evidence_refs_item_data in self.evidence_refs:
            evidence_refs_item = evidence_refs_item_data.to_dict()
            evidence_refs.append(evidence_refs_item)

        finding_id = str(self.finding_id)

        impact = self.impact

        lane: Literal["CODE"] | Literal["ENVIRONMENT"]
        lane = self.lane

        lifecycle_state = self.lifecycle_state.value

        organization_id = str(self.organization_id)

        review_id = str(self.review_id)

        risk_domain = self.risk_domain

        severity = self.severity.value

        environment_id: None | str | Unset
        if isinstance(self.environment_id, Unset):
            environment_id = UNSET
        elif isinstance(self.environment_id, UUID):
            environment_id = str(self.environment_id)
        else:
            environment_id = self.environment_id

        remediation: None | str | Unset
        if isinstance(self.remediation, Unset):
            remediation = UNSET
        else:
            remediation = self.remediation

        repository_id: None | str | Unset
        if isinstance(self.repository_id, Unset):
            repository_id = UNSET
        elif isinstance(self.repository_id, UUID):
            repository_id = str(self.repository_id)
        else:
            repository_id = self.repository_id

        series_id: None | str | Unset
        if isinstance(self.series_id, Unset):
            series_id = UNSET
        elif isinstance(self.series_id, UUID):
            series_id = str(self.series_id)
        else:
            series_id = self.series_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_id": assessment_id,
                "claim": claim,
                "created_at": created_at,
                "dataset_version": dataset_version,
                "evidence_refs": evidence_refs,
                "finding_id": finding_id,
                "impact": impact,
                "lane": lane,
                "lifecycle_state": lifecycle_state,
                "organization_id": organization_id,
                "review_id": review_id,
                "risk_domain": risk_domain,
                "severity": severity,
            }
        )
        if environment_id is not UNSET:
            field_dict["environment_id"] = environment_id
        if remediation is not UNSET:
            field_dict["remediation"] = remediation
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if series_id is not UNSET:
            field_dict["series_id"] = series_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.export_evidence_ref import ExportEvidenceRef  # noqa: PLC0415

        d = dict(src_dict)
        assessment_id = UUID(d.pop("assessment_id"))

        claim = d.pop("claim")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        dataset_version = d.pop("dataset_version")

        evidence_refs = []
        _evidence_refs = d.pop("evidence_refs")
        for evidence_refs_item_data in _evidence_refs:
            evidence_refs_item = ExportEvidenceRef.from_dict(evidence_refs_item_data)

            evidence_refs.append(evidence_refs_item)

        finding_id = UUID(d.pop("finding_id"))

        impact = d.pop("impact")

        def _parse_lane(data: object) -> Literal["CODE"] | Literal["ENVIRONMENT"]:
            try:
                if not (type(data) is str and data == "ENVIRONMENT"):
                    raise TypeError()
                componentsschemas_export_finding_lane_type_0 = cast(Literal["ENVIRONMENT"], data)
                if componentsschemas_export_finding_lane_type_0 != "ENVIRONMENT":
                    raise ValueError(
                        f"/components/schemas/ExportFindingLane_type_0 must match const 'ENVIRONMENT', got '{componentsschemas_export_finding_lane_type_0}'"
                    )
                return componentsschemas_export_finding_lane_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "CODE"):
                raise TypeError()
            componentsschemas_export_finding_lane_type_1 = cast(Literal["CODE"], data)
            if componentsschemas_export_finding_lane_type_1 != "CODE":
                raise ValueError(
                    f"/components/schemas/ExportFindingLane_type_1 must match const 'CODE', got '{componentsschemas_export_finding_lane_type_1}'"
                )
            return componentsschemas_export_finding_lane_type_1

        lane = _parse_lane(d.pop("lane"))

        lifecycle_state = ExportFindingLifecycle(d.pop("lifecycle_state"))

        organization_id = UUID(d.pop("organization_id"))

        review_id = UUID(d.pop("review_id"))

        risk_domain = d.pop("risk_domain")

        severity = ExportFindingSeverity(d.pop("severity"))

        def _parse_environment_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                environment_id_type_0 = UUID(data)

                return environment_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        environment_id = _parse_environment_id(d.pop("environment_id", UNSET))

        def _parse_remediation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        remediation = _parse_remediation(d.pop("remediation", UNSET))

        def _parse_repository_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repository_id_type_0 = UUID(data)

                return repository_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        repository_id = _parse_repository_id(d.pop("repository_id", UNSET))

        def _parse_series_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                series_id_type_0 = UUID(data)

                return series_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        series_id = _parse_series_id(d.pop("series_id", UNSET))

        findings_export_row = cls(
            assessment_id=assessment_id,
            claim=claim,
            created_at=created_at,
            dataset_version=dataset_version,
            evidence_refs=evidence_refs,
            finding_id=finding_id,
            impact=impact,
            lane=lane,
            lifecycle_state=lifecycle_state,
            organization_id=organization_id,
            review_id=review_id,
            risk_domain=risk_domain,
            severity=severity,
            environment_id=environment_id,
            remediation=remediation,
            repository_id=repository_id,
            series_id=series_id,
        )

        findings_export_row.additional_properties = d
        return findings_export_row

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
