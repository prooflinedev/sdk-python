from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewDiffStats")


@_attrs_define
class ReviewDiffStats:
    """
    Attributes:
        additions (int): Lines added across every changed file in the pinned comparison.
        deletions (int): Lines deleted across every changed file in the pinned comparison.
    """

    additions: int
    deletions: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        additions = self.additions

        deletions = self.deletions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "additions": additions,
                "deletions": deletions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        additions = d.pop("additions")

        deletions = d.pop("deletions")

        review_diff_stats = cls(
            additions=additions,
            deletions=deletions,
        )

        review_diff_stats.additional_properties = d
        return review_diff_stats

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
