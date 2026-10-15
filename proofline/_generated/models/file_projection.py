from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileProjection")


@_attrs_define
class FileProjection:
    """
    Attributes:
        depth (str): The code-inspection depth retained by the plan.
        passes (list[str]): The review passes bound to this file.
        path (str): Repository-relative path retained by the routing plan.
    """

    depth: str
    passes: list[str]
    path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        depth = self.depth

        passes = self.passes

        path = self.path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "depth": depth,
                "passes": passes,
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        depth = d.pop("depth")

        passes = cast(list[str], d.pop("passes"))

        path = d.pop("path")

        file_projection = cls(
            depth=depth,
            passes=passes,
            path=path,
        )

        file_projection.additional_properties = d
        return file_projection

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
