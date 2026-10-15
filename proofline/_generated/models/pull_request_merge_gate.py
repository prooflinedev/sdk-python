from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.gate_status import GateStatus
from ..models.outcome import Outcome
from ..types import UNSET, Unset

T = TypeVar("T", bound="PullRequestMergeGate")


@_attrs_define
class PullRequestMergeGate:
    """
    Attributes:
        blocking_severity (str): The frozen blocking threshold, either SERIOUS or WARNING; later settings do not restamp
            it.
        head_sha (str): The exact lowercase commit SHA whose captured policy this gate evaluates.
        id (UUID): The immutable identity of the gate captured for this tenant, repository and head.
        policy_version (str): The deterministic policy version frozen when this gate was captured.
        pull_request_number (int): The first pull request that captured this head's gate; a shared-head merge may name
            another PR.
        status (GateStatus):
        assessment_count (int | None | Unset): The number of environment assessments counted by the recorded decision.
            Null before a decision.
        bypassed_at (datetime.datetime | None | Unset): When the bypass receipt was recorded. Null when this gate has no
            recorded bypass.
        coverage_digest (None | str | Unset): The digest of the deterministic coverage used by the decision, or null
            when no digest was recorded.
        decided_at (datetime.datetime | None | Unset): When the immutable decision was recorded. Null before a decision.
        decision (None | Outcome | Unset): The immutable ALLOW or BLOCK decision. Null until a decision is recorded.
        finding_count (int | None | Unset): The number of blocking findings counted by the recorded decision. Null
            before a decision.
        merge_commit_sha (None | str | Unset): The exact merge commit reported by GitHub for the bypass, or null when
            none was reported.
        merged_by_github_user_id (int | None | Unset): The stable GitHub user ID reported by a merged-close bypass, or
            null when none was reported.
        merged_pull_request_number (int | None | Unset): The actual pull request merged in the recorded bypass, which
            may differ from the captured PR.
        reason_code (None | str | Unset): The recorded deterministic decision or refusal reason. Null until a decision
            is recorded.
        review_id (None | Unset | UUID): The first review captured for this gate. Null when its trigger was refused
            before a review existed.
    """

    blocking_severity: str
    head_sha: str
    id: UUID
    policy_version: str
    pull_request_number: int
    status: GateStatus
    assessment_count: int | None | Unset = UNSET
    bypassed_at: datetime.datetime | None | Unset = UNSET
    coverage_digest: None | str | Unset = UNSET
    decided_at: datetime.datetime | None | Unset = UNSET
    decision: None | Outcome | Unset = UNSET
    finding_count: int | None | Unset = UNSET
    merge_commit_sha: None | str | Unset = UNSET
    merged_by_github_user_id: int | None | Unset = UNSET
    merged_pull_request_number: int | None | Unset = UNSET
    reason_code: None | str | Unset = UNSET
    review_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        blocking_severity = self.blocking_severity

        head_sha = self.head_sha

        id = str(self.id)

        policy_version = self.policy_version

        pull_request_number = self.pull_request_number

        status = self.status.value

        assessment_count: int | None | Unset
        if isinstance(self.assessment_count, Unset):
            assessment_count = UNSET
        else:
            assessment_count = self.assessment_count

        bypassed_at: None | str | Unset
        if isinstance(self.bypassed_at, Unset):
            bypassed_at = UNSET
        elif isinstance(self.bypassed_at, datetime.datetime):
            bypassed_at = self.bypassed_at.isoformat()
        else:
            bypassed_at = self.bypassed_at

        coverage_digest: None | str | Unset
        if isinstance(self.coverage_digest, Unset):
            coverage_digest = UNSET
        else:
            coverage_digest = self.coverage_digest

        decided_at: None | str | Unset
        if isinstance(self.decided_at, Unset):
            decided_at = UNSET
        elif isinstance(self.decided_at, datetime.datetime):
            decided_at = self.decided_at.isoformat()
        else:
            decided_at = self.decided_at

        decision: None | str | Unset
        if isinstance(self.decision, Unset):
            decision = UNSET
        elif isinstance(self.decision, Outcome):
            decision = self.decision.value
        else:
            decision = self.decision

        finding_count: int | None | Unset
        if isinstance(self.finding_count, Unset):
            finding_count = UNSET
        else:
            finding_count = self.finding_count

        merge_commit_sha: None | str | Unset
        if isinstance(self.merge_commit_sha, Unset):
            merge_commit_sha = UNSET
        else:
            merge_commit_sha = self.merge_commit_sha

        merged_by_github_user_id: int | None | Unset
        if isinstance(self.merged_by_github_user_id, Unset):
            merged_by_github_user_id = UNSET
        else:
            merged_by_github_user_id = self.merged_by_github_user_id

        merged_pull_request_number: int | None | Unset
        if isinstance(self.merged_pull_request_number, Unset):
            merged_pull_request_number = UNSET
        else:
            merged_pull_request_number = self.merged_pull_request_number

        reason_code: None | str | Unset
        if isinstance(self.reason_code, Unset):
            reason_code = UNSET
        else:
            reason_code = self.reason_code

        review_id: None | str | Unset
        if isinstance(self.review_id, Unset):
            review_id = UNSET
        elif isinstance(self.review_id, UUID):
            review_id = str(self.review_id)
        else:
            review_id = self.review_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "blocking_severity": blocking_severity,
                "head_sha": head_sha,
                "id": id,
                "policy_version": policy_version,
                "pull_request_number": pull_request_number,
                "status": status,
            }
        )
        if assessment_count is not UNSET:
            field_dict["assessment_count"] = assessment_count
        if bypassed_at is not UNSET:
            field_dict["bypassed_at"] = bypassed_at
        if coverage_digest is not UNSET:
            field_dict["coverage_digest"] = coverage_digest
        if decided_at is not UNSET:
            field_dict["decided_at"] = decided_at
        if decision is not UNSET:
            field_dict["decision"] = decision
        if finding_count is not UNSET:
            field_dict["finding_count"] = finding_count
        if merge_commit_sha is not UNSET:
            field_dict["merge_commit_sha"] = merge_commit_sha
        if merged_by_github_user_id is not UNSET:
            field_dict["merged_by_github_user_id"] = merged_by_github_user_id
        if merged_pull_request_number is not UNSET:
            field_dict["merged_pull_request_number"] = merged_pull_request_number
        if reason_code is not UNSET:
            field_dict["reason_code"] = reason_code
        if review_id is not UNSET:
            field_dict["review_id"] = review_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        blocking_severity = d.pop("blocking_severity")

        head_sha = d.pop("head_sha")

        id = UUID(d.pop("id"))

        policy_version = d.pop("policy_version")

        pull_request_number = d.pop("pull_request_number")

        status = GateStatus(d.pop("status"))

        def _parse_assessment_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        assessment_count = _parse_assessment_count(d.pop("assessment_count", UNSET))

        def _parse_bypassed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                bypassed_at_type_0 = datetime.datetime.fromisoformat(data)

                return bypassed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        bypassed_at = _parse_bypassed_at(d.pop("bypassed_at", UNSET))

        def _parse_coverage_digest(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        coverage_digest = _parse_coverage_digest(d.pop("coverage_digest", UNSET))

        def _parse_decided_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                decided_at_type_0 = datetime.datetime.fromisoformat(data)

                return decided_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        decided_at = _parse_decided_at(d.pop("decided_at", UNSET))

        def _parse_decision(data: object) -> None | Outcome | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                decision_type_0 = Outcome(data)

                return decision_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Outcome | Unset, data)

        decision = _parse_decision(d.pop("decision", UNSET))

        def _parse_finding_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        finding_count = _parse_finding_count(d.pop("finding_count", UNSET))

        def _parse_merge_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        merge_commit_sha = _parse_merge_commit_sha(d.pop("merge_commit_sha", UNSET))

        def _parse_merged_by_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        merged_by_github_user_id = _parse_merged_by_github_user_id(
            d.pop("merged_by_github_user_id", UNSET)
        )

        def _parse_merged_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        merged_pull_request_number = _parse_merged_pull_request_number(
            d.pop("merged_pull_request_number", UNSET)
        )

        def _parse_reason_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason_code = _parse_reason_code(d.pop("reason_code", UNSET))

        def _parse_review_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                review_id_type_0 = UUID(data)

                return review_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        review_id = _parse_review_id(d.pop("review_id", UNSET))

        pull_request_merge_gate = cls(
            blocking_severity=blocking_severity,
            head_sha=head_sha,
            id=id,
            policy_version=policy_version,
            pull_request_number=pull_request_number,
            status=status,
            assessment_count=assessment_count,
            bypassed_at=bypassed_at,
            coverage_digest=coverage_digest,
            decided_at=decided_at,
            decision=decision,
            finding_count=finding_count,
            merge_commit_sha=merge_commit_sha,
            merged_by_github_user_id=merged_by_github_user_id,
            merged_pull_request_number=merged_pull_request_number,
            reason_code=reason_code,
            review_id=review_id,
        )

        pull_request_merge_gate.additional_properties = d
        return pull_request_merge_gate

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
