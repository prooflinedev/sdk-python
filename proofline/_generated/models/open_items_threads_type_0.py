from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OpenItemsThreadsType0")


@_attrs_define
class OpenItemsThreadsType0:
    """
    Attributes:
        observed_at (datetime.datetime):
        status (Literal['KNOWN']):
        unresolved_count (int):
        unresolved_urls (list[str] | Unset): Root comment URLs for the unresolved Proofline threads in this observation.
    """

    observed_at: datetime.datetime
    status: Literal["KNOWN"]
    unresolved_count: int
    unresolved_urls: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        observed_at = self.observed_at.isoformat()

        status = self.status

        unresolved_count = self.unresolved_count

        unresolved_urls: list[str] | Unset = UNSET
        if not isinstance(self.unresolved_urls, Unset):
            unresolved_urls = self.unresolved_urls

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "observed_at": observed_at,
                "status": status,
                "unresolved_count": unresolved_count,
            }
        )
        if unresolved_urls is not UNSET:
            field_dict["unresolved_urls"] = unresolved_urls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        observed_at = datetime.datetime.fromisoformat(d.pop("observed_at"))

        status = cast(Literal["KNOWN"], d.pop("status"))
        if status != "KNOWN":
            raise ValueError(f"status must match const 'KNOWN', got '{status}'")

        unresolved_count = d.pop("unresolved_count")

        unresolved_urls = cast(list[str], d.pop("unresolved_urls", UNSET))

        open_items_threads_type_0 = cls(
            observed_at=observed_at,
            status=status,
            unresolved_count=unresolved_count,
            unresolved_urls=unresolved_urls,
        )

        open_items_threads_type_0.additional_properties = d
        return open_items_threads_type_0

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
