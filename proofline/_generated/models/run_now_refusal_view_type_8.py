from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunNowRefusalViewType8")


@_attrs_define
class RunNowRefusalViewType8:
    """The pull request's author holds no seat: seat settings.

    Attributes:
        reason (Literal['AUTHOR_HAS_NO_SEAT']):
    """

    reason: Literal["AUTHOR_HAS_NO_SEAT"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reason = cast(Literal["AUTHOR_HAS_NO_SEAT"], d.pop("reason"))
        if reason != "AUTHOR_HAS_NO_SEAT":
            raise ValueError(f"reason must match const 'AUTHOR_HAS_NO_SEAT', got '{reason}'")

        run_now_refusal_view_type_8 = cls(
            reason=reason,
        )

        run_now_refusal_view_type_8.additional_properties = d
        return run_now_refusal_view_type_8

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
