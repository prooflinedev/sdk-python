from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.rule_source import RuleSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="FindingRuleRevisionView")


@_attrs_define
class FindingRuleRevisionView:
    """
    Attributes:
        scope (str): `ORGANIZATION`, `ENVIRONMENT`, `TEAM` or `REPOSITORY`.
        source (RuleSource):
        revision (int | None | Unset): The console revision. Null for a configuration-file or implicit rule.
    """

    scope: str
    source: RuleSource
    revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scope = self.scope

        source = self.source.value

        revision: int | None | Unset
        if isinstance(self.revision, Unset):
            revision = UNSET
        else:
            revision = self.revision

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        finding_rule_revision_view = cls(
            scope=scope,
            source=source,
            revision=revision,
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
