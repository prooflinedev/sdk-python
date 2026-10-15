from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewRoutingViewType1")


@_attrs_define
class ReviewRoutingViewType1:
    """A routing plan exists, but this server does not decode its version.

    Attributes:
        status (Literal['UNSUPPORTED']):
        version (str): Version identifier stored with the plan.
    """

    status: Literal["UNSUPPORTED"]
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = cast(Literal["UNSUPPORTED"], d.pop("status"))
        if status != "UNSUPPORTED":
            raise ValueError(f"status must match const 'UNSUPPORTED', got '{status}'")

        version = d.pop("version")

        review_routing_view_type_1 = cls(
            status=status,
            version=version,
        )

        review_routing_view_type_1.additional_properties = d
        return review_routing_view_type_1

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
