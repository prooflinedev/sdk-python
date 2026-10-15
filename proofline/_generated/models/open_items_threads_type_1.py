from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.open_items_thread_unknown import OpenItemsThreadUnknown

T = TypeVar("T", bound="OpenItemsThreadsType1")


@_attrs_define
class OpenItemsThreadsType1:
    """
    Attributes:
        reason (OpenItemsThreadUnknown):
        status (Literal['UNKNOWN']):
    """

    reason: OpenItemsThreadUnknown
    status: Literal["UNKNOWN"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason.value

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reason = OpenItemsThreadUnknown(d.pop("reason"))

        status = cast(Literal["UNKNOWN"], d.pop("status"))
        if status != "UNKNOWN":
            raise ValueError(f"status must match const 'UNKNOWN', got '{status}'")

        open_items_threads_type_1 = cls(
            reason=reason,
            status=status,
        )

        open_items_threads_type_1.additional_properties = d
        return open_items_threads_type_1

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
