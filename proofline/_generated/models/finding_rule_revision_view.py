from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.rule_source import RuleSource
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.finding_rule_incident_view import FindingRuleIncidentView


T = TypeVar("T", bound="FindingRuleRevisionView")


@_attrs_define
class FindingRuleRevisionView:
    """
    Attributes:
        scope (str): `ORGANIZATION`, `ENVIRONMENT`, `TEAM` or `REPOSITORY`.
        source (RuleSource):
        revision (int | None | Unset): The console revision. Null for a configuration-file or implicit rule.
        incident (FindingRuleIncidentView | None | Unset): The incident a prevention rule came from. Absent for every
            other rule.
    """

    scope: str
    source: RuleSource
    revision: int | None | Unset = UNSET
    incident: FindingRuleIncidentView | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.finding_rule_incident_view import FindingRuleIncidentView  # noqa: PLC0415

        scope = self.scope

        source = self.source.value

        revision: int | None | Unset
        if isinstance(self.revision, Unset):
            revision = UNSET
        else:
            revision = self.revision

        incident: dict[str, Any] | None | Unset
        if isinstance(self.incident, Unset):
            incident = UNSET
        elif isinstance(self.incident, FindingRuleIncidentView):
            incident = self.incident.to_dict()
        else:
            incident = self.incident

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
                "source": source,
            }
        )
        if revision is not UNSET:
            field_dict["revision"] = revision
        if incident is not UNSET:
            field_dict["incident"] = incident

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_rule_incident_view import FindingRuleIncidentView  # noqa: PLC0415

        d = dict(src_dict)
        scope = d.pop("scope")

        source = RuleSource(d.pop("source"))

        def _parse_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        revision = _parse_revision(d.pop("revision", UNSET))

        def _parse_incident(data: object) -> FindingRuleIncidentView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                incident_type_0 = FindingRuleIncidentView.from_dict(data)

                return incident_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingRuleIncidentView | None | Unset, data)

        incident = _parse_incident(d.pop("incident", UNSET))

        finding_rule_revision_view = cls(
            scope=scope,
            source=source,
            revision=revision,
            incident=incident,
        )

        finding_rule_revision_view.additional_properties = d
        return finding_rule_revision_view

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
