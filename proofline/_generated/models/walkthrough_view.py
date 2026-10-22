from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.walkthrough_group_view import WalkthroughGroupView


T = TypeVar("T", bound="WalkthroughView")


@_attrs_define
class WalkthroughView:
    """One review's walkthrough of its pinned head. Titles and lines are model
    text over untrusted repository content: render them as text.

       Attributes:
           groups (list[WalkthroughGroupView]): Groups in reading order.
           head_sha (str):
    """

    groups: list[WalkthroughGroupView]
    head_sha: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        head_sha = self.head_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "groups": groups,
                "head_sha": head_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.walkthrough_group_view import WalkthroughGroupView  # noqa: PLC0415

        d = dict(src_dict)
        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = WalkthroughGroupView.from_dict(groups_item_data)

            groups.append(groups_item)

        head_sha = d.pop("head_sha")

        walkthrough_view = cls(
            groups=groups,
            head_sha=head_sha,
        )

        walkthrough_view.additional_properties = d
        return walkthrough_view

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
