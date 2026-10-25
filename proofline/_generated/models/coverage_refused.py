from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CoverageRefused")


@_attrs_define
class CoverageRefused:
    """An upload refused for its content: a symbolic or unknown commit, or a
    report that cannot be read. Nothing is stored.

       Attributes:
           detail (str): One sentence naming what was refused and why.
           status (int): Always 422.
           title (str): Always `unprocessable coverage upload`.
    """

    detail: str
    status: int
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        detail = self.detail

        status = self.status

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
                "status": status,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        detail = d.pop("detail")

        status = d.pop("status")

        title = d.pop("title")

        coverage_refused = cls(
            detail=detail,
            status=status,
            title=title,
        )

        coverage_refused.additional_properties = d
        return coverage_refused

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
