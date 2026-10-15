from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.finding_rule_revision_view import FindingRuleRevisionView


T = TypeVar("T", bound="FindingRuleRefView")


@_attrs_define
class FindingRuleRefView:
    """One review rule a finding cites. It carries no rule text and no scope
    identifier; the review rules page shows those to its readers.

       Attributes:
           key (str): The rule key.
           revisions (list[FindingRuleRevisionView]): The layers of the key the assessment showed the reviewer, in
                precedence order. A team rule is a layer over the key for the files it
                matches.
    """

    key: str
    revisions: list[FindingRuleRevisionView]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        revisions = []
        for revisions_item_data in self.revisions:
            revisions_item = revisions_item_data.to_dict()
            revisions.append(revisions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "revisions": revisions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_rule_revision_view import FindingRuleRevisionView  # noqa: PLC0415

        d = dict(src_dict)
        key = d.pop("key")

        revisions = []
        _revisions = d.pop("revisions")
        for revisions_item_data in _revisions:
            revisions_item = FindingRuleRevisionView.from_dict(revisions_item_data)

            revisions.append(revisions_item)

        finding_rule_ref_view = cls(
            key=key,
            revisions=revisions,
        )

        finding_rule_ref_view.additional_properties = d
        return finding_rule_ref_view

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
