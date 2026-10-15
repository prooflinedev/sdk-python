from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SpecialistOutputProjection")


@_attrs_define
class SpecialistOutputProjection:
    """A pass receipt's bounded operational facts, without its proposals or prose.

    Attributes:
        output_sha256 (str): Verified digest of the retained output bytes.
        status (str): `PRODUCED`, `UNAVAILABLE`, `INCOMPLETE` or `MALFORMED`.
        gap_kind (None | str | Unset): Closed evidence-gap class, absent when the pass produced output.
    """

    output_sha256: str
    status: str
    gap_kind: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_sha256 = self.output_sha256

        status = self.status

        gap_kind: None | str | Unset
        if isinstance(self.gap_kind, Unset):
            gap_kind = UNSET
        else:
            gap_kind = self.gap_kind

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "output_sha256": output_sha256,
                "status": status,
            }
        )
        if gap_kind is not UNSET:
            field_dict["gap_kind"] = gap_kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        output_sha256 = d.pop("output_sha256")

        status = d.pop("status")

        def _parse_gap_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        gap_kind = _parse_gap_kind(d.pop("gap_kind", UNSET))

        specialist_output_projection = cls(
            output_sha256=output_sha256,
            status=status,
            gap_kind=gap_kind,
        )

        specialist_output_projection.additional_properties = d
        return specialist_output_projection

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
