from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotAssessedView")


@_attrs_define
class NotAssessedView:
    """
    Attributes:
        environment_display_name (str): The display name of the environment whose assessment is not
             `COMPLETED`.
        incompleteness_kind (None | str | Unset): The assessment's recorded gap class. Absent is an unclassified gap,
             never a complete assessment.
    """

    environment_display_name: str
    incompleteness_kind: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_display_name = self.environment_display_name

        incompleteness_kind: None | str | Unset
        if isinstance(self.incompleteness_kind, Unset):
            incompleteness_kind = UNSET
        else:
            incompleteness_kind = self.incompleteness_kind

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_display_name": environment_display_name,
            }
        )
        if incompleteness_kind is not UNSET:
            field_dict["incompleteness_kind"] = incompleteness_kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        environment_display_name = d.pop("environment_display_name")

        def _parse_incompleteness_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        incompleteness_kind = _parse_incompleteness_kind(d.pop("incompleteness_kind", UNSET))

        not_assessed_view = cls(
            environment_display_name=environment_display_name,
            incompleteness_kind=incompleteness_kind,
        )

        not_assessed_view.additional_properties = d
        return not_assessed_view

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
