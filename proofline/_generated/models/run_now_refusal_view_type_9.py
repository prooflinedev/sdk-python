from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunNowRefusalViewType9")


@_attrs_define
class RunNowRefusalViewType9:
    """The pull request closed between GitHub's answer that it was open and
    the review's creation. Nothing to change; the pull request itself.

       Attributes:
           reason (Literal['PULL_REQUEST_CLOSED']):
    """

    reason: Literal["PULL_REQUEST_CLOSED"]
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
        reason = cast(Literal["PULL_REQUEST_CLOSED"], d.pop("reason"))
        if reason != "PULL_REQUEST_CLOSED":
            raise ValueError(f"reason must match const 'PULL_REQUEST_CLOSED', got '{reason}'")

        run_now_refusal_view_type_9 = cls(
            reason=reason,
        )

        run_now_refusal_view_type_9.additional_properties = d
        return run_now_refusal_view_type_9

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
