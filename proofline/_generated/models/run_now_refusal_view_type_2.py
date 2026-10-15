from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunNowRefusalViewType2")


@_attrs_define
class RunNowRefusalViewType2:
    """No environment links this repository: the repository's setup.

    Attributes:
        reason (Literal['NO_LINKED_ENVIRONMENT']):
    """

    reason: Literal["NO_LINKED_ENVIRONMENT"]
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
        reason = cast(Literal["NO_LINKED_ENVIRONMENT"], d.pop("reason"))
        if reason != "NO_LINKED_ENVIRONMENT":
            raise ValueError(f"reason must match const 'NO_LINKED_ENVIRONMENT', got '{reason}'")

        run_now_refusal_view_type_2 = cls(
            reason=reason,
        )

        run_now_refusal_view_type_2.additional_properties = d
        return run_now_refusal_view_type_2

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
