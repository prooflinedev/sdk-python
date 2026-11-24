from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModelWarning")


@_attrs_define
class ModelWarning:
    """Why a review started now would run without its model.

    Attributes:
        cause (str): Proofline's sentence naming the fix.
        reason_code (str): `MODEL_<cause>`, the same code a finished review's read carries.
    """

    cause: str
    reason_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cause = self.cause

        reason_code = self.reason_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cause": cause,
                "reason_code": reason_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cause = d.pop("cause")

        reason_code = d.pop("reason_code")

        model_warning = cls(
            cause=cause,
            reason_code=reason_code,
        )

        model_warning.additional_properties = d
        return model_warning

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
