from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OpenFindingCounts")


@_attrs_define
class OpenFindingCounts:
    """
    Attributes:
        serious (int): Finding series with `SERIOUS` severity that are unresolved and not
             under an unexpired dismissal or risk acceptance.
        warning (int): Finding series with `WARNING` severity that are unresolved and not
             under an unexpired dismissal or risk acceptance.
    """

    serious: int
    warning: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        serious = self.serious

        warning = self.warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "serious": serious,
                "warning": warning,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        serious = d.pop("serious")

        warning = d.pop("warning")

        open_finding_counts = cls(
            serious=serious,
            warning=warning,
        )

        open_finding_counts.additional_properties = d
        return open_finding_counts

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
