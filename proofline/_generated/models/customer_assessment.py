from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_checks import CustomerChecks
    from ..models.customer_decision import CustomerDecision
    from ..models.customer_finding import CustomerFinding
    from ..models.domain_view import DomainView


T = TypeVar("T", bound="CustomerAssessment")


@_attrs_define
class CustomerAssessment:
    """
    Attributes:
        checks (CustomerChecks):
        domains (list[DomainView]): The risk domains the assessment evaluated, each with its status and
             reason, ordered by domain.
        environment_display_name (str): The display name of the environment this assessment covers.
        findings (list[CustomerFinding]): The findings this assessment recorded, `SERIOUS` first.
        id (UUID): The assessment's ID.
        status (str): The assessment's recorded status, such as `RUNNING`, `COMPLETED` or
             `INCOMPLETE`.
        completed_at (datetime.datetime | None | Unset): When the assessment completed. Null while it has not.
        decision_presentation (CustomerDecision | None | Unset): The retained decision disclosure, which grants no
            deployment
             authorization. Absent when none is recorded and the review kind
             records no decision basis.
        incompleteness_kind (None | str | Unset): Why an `INCOMPLETE` assessment is incomplete: `NOT_CONFIGURED`,
             `POLICY_EXCLUDED`, `EVIDENCE_UNAVAILABLE`, `HYPOTHESES_UNRESOLVED` or
             `MODEL_BUDGET_EXHAUSTED`. Absent otherwise; an unclassified gap is not a
             complete assessment.
        reason_codes (list[str] | None | Unset): Public assessment gap codes. A recorded out-of-credits refusal
             is projected as `OUT_OF_CREDITS` when no stored code exists. Other
             historical records may have no codes; private details are not exposed.
        release_evidence_gap (None | str | Unset): The typed gap the automatic release-set read recorded. Null when the
             read is pending, pinned a release, or was never attempted.
        started_at (datetime.datetime | None | Unset): When the assessment started. Null until it starts.
    """

    checks: CustomerChecks
    domains: list[DomainView]
    environment_display_name: str
    findings: list[CustomerFinding]
    id: UUID
    status: str
    completed_at: datetime.datetime | None | Unset = UNSET
    decision_presentation: CustomerDecision | None | Unset = UNSET
    incompleteness_kind: None | str | Unset = UNSET
    reason_codes: list[str] | None | Unset = UNSET
    release_evidence_gap: None | str | Unset = UNSET
    started_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_decision import CustomerDecision  # noqa: PLC0415

        checks = self.checks.to_dict()

        domains = []
        for domains_item_data in self.domains:
            domains_item = domains_item_data.to_dict()
            domains.append(domains_item)

        environment_display_name = self.environment_display_name

        findings = []
        for findings_item_data in self.findings:
            findings_item = findings_item_data.to_dict()
            findings.append(findings_item)

        id = str(self.id)

        status = self.status

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        decision_presentation: dict[str, Any] | None | Unset
        if isinstance(self.decision_presentation, Unset):
            decision_presentation = UNSET
        elif isinstance(self.decision_presentation, CustomerDecision):
            decision_presentation = self.decision_presentation.to_dict()
        else:
            decision_presentation = self.decision_presentation

        incompleteness_kind: None | str | Unset
        if isinstance(self.incompleteness_kind, Unset):
            incompleteness_kind = UNSET
        else:
            incompleteness_kind = self.incompleteness_kind

        reason_codes: list[str] | None | Unset
        if isinstance(self.reason_codes, Unset):
            reason_codes = UNSET
        elif isinstance(self.reason_codes, list):
            reason_codes = self.reason_codes

        else:
            reason_codes = self.reason_codes

        release_evidence_gap: None | str | Unset
        if isinstance(self.release_evidence_gap, Unset):
            release_evidence_gap = UNSET
        else:
            release_evidence_gap = self.release_evidence_gap

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
                "checks": checks,
                "domains": domains,
                "environment_display_name": environment_display_name,
                "findings": findings,
                "id": id,
                "status": status,
            }
        )
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if decision_presentation is not UNSET:
            field_dict["decision_presentation"] = decision_presentation
        if incompleteness_kind is not UNSET:
            field_dict["incompleteness_kind"] = incompleteness_kind
        if reason_codes is not UNSET:
            field_dict["reason_codes"] = reason_codes
        if release_evidence_gap is not UNSET:
            field_dict["release_evidence_gap"] = release_evidence_gap
        if started_at is not UNSET:
            field_dict["started_at"] = started_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_checks import CustomerChecks  # noqa: PLC0415
        from ..models.customer_decision import CustomerDecision  # noqa: PLC0415
        from ..models.customer_finding import CustomerFinding  # noqa: PLC0415
        from ..models.domain_view import DomainView  # noqa: PLC0415

        d = dict(src_dict)
        checks = CustomerChecks.from_dict(d.pop("checks"))

        domains = []
        _domains = d.pop("domains")
        for domains_item_data in _domains:
            domains_item = DomainView.from_dict(domains_item_data)

            domains.append(domains_item)

        environment_display_name = d.pop("environment_display_name")

        findings = []
        _findings = d.pop("findings")
        for findings_item_data in _findings:
            findings_item = CustomerFinding.from_dict(findings_item_data)

            findings.append(findings_item)

        id = UUID(d.pop("id"))

        status = d.pop("status")

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

        def _parse_decision_presentation(data: object) -> CustomerDecision | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_presentation_type_0 = CustomerDecision.from_dict(data)

                return decision_presentation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerDecision | None | Unset, data)

        decision_presentation = _parse_decision_presentation(d.pop("decision_presentation", UNSET))

        def _parse_incompleteness_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        incompleteness_kind = _parse_incompleteness_kind(d.pop("incompleteness_kind", UNSET))

        def _parse_reason_codes(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                reason_codes_type_0 = cast(list[str], data)

                return reason_codes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        reason_codes = _parse_reason_codes(d.pop("reason_codes", UNSET))

        def _parse_release_evidence_gap(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        release_evidence_gap = _parse_release_evidence_gap(d.pop("release_evidence_gap", UNSET))

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

        customer_assessment = cls(
            checks=checks,
            domains=domains,
            environment_display_name=environment_display_name,
            findings=findings,
            id=id,
            status=status,
            completed_at=completed_at,
            decision_presentation=decision_presentation,
            incompleteness_kind=incompleteness_kind,
            reason_codes=reason_codes,
            release_evidence_gap=release_evidence_gap,
            started_at=started_at,
        )

        customer_assessment.additional_properties = d
        return customer_assessment

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
