from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FindingCausalNodeView")


@_attrs_define
class FindingCausalNodeView:
    """
    Attributes:
        id (str): The reviewer-assigned node identifier that edges refer to. Model-authored text.
        label (str): What the node is. Model-authored text: render as text.
        role (str): One of `change`, `dependency`, `failure`, `blocked` or `ok`, or empty; a value outside that set is
            returned as recorded.
    """

    id: str
    label: str
    role: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        role = self.role

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "label": label,
                "role": role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        role = d.pop("role")

        finding_causal_node_view = cls(
            id=id,
            label=label,
            role=role,
        )

        finding_causal_node_view.additional_properties = d
        return finding_causal_node_view

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
