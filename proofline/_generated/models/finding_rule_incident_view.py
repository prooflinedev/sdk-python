from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FindingRuleIncidentView")


@_attrs_define
class FindingRuleIncidentView:
    """The incident behind a cited prevention rule, as the finding's assessment
    pinned it.

       Attributes:
           check (str): What the assessment's pinned Kian view showed of that condition.
           commit_sha (str): The commit the incident's confirmed cause names.
           condition (str): What the incident needed in the environment.
           investigation_id (UUID):
    """

    check: str
    commit_sha: str
    condition: str
    investigation_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        check = self.check

        commit_sha = self.commit_sha

        condition = self.condition

        investigation_id = str(self.investigation_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "check": check,
                "commit_sha": commit_sha,
                "condition": condition,
                "investigation_id": investigation_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        check = d.pop("check")

        commit_sha = d.pop("commit_sha")

        condition = d.pop("condition")

        investigation_id = UUID(d.pop("investigation_id"))

        finding_rule_incident_view = cls(
            check=check,
            commit_sha=commit_sha,
            condition=condition,
            investigation_id=investigation_id,
        )

        finding_rule_incident_view.additional_properties = d
        return finding_rule_incident_view

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
