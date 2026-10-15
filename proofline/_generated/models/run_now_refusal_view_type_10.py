from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunNowRefusalViewType10")


@_attrs_define
class RunNowRefusalViewType10:
    """Deep review policy, funding or worker availability prevents admission.

    Attributes:
        detail (str):
        reason (Literal['DEEP_REVIEW_UNAVAILABLE']):
    """

    detail: str
    reason: Literal["DEEP_REVIEW_UNAVAILABLE"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        detail = self.detail

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        detail = d.pop("detail")

        reason = cast(Literal["DEEP_REVIEW_UNAVAILABLE"], d.pop("reason"))
        if reason != "DEEP_REVIEW_UNAVAILABLE":
            raise ValueError(f"reason must match const 'DEEP_REVIEW_UNAVAILABLE', got '{reason}'")

        run_now_refusal_view_type_10 = cls(
            detail=detail,
            reason=reason,
        )

        run_now_refusal_view_type_10.additional_properties = d
        return run_now_refusal_view_type_10

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
