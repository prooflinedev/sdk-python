from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.specialist_output_projection import SpecialistOutputProjection


T = TypeVar("T", bound="SpecialistPassExecution")


@_attrs_define
class SpecialistPassExecution:
    """
    Attributes:
        files (list[str]): Exact selected paths from the validated captured change.
        floor (bool): Whether captured file facts required this pass.
        name (str): Closed registry key of the selected specialist.
        output (None | SpecialistOutputProjection | Unset): Missing means selected, with no retained output. It never
            means success.
    """

    files: list[str]
    floor: bool
    name: str
    output: None | SpecialistOutputProjection | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.specialist_output_projection import (
            SpecialistOutputProjection,  # noqa: PLC0415
        )

        files = self.files

        floor = self.floor

        name = self.name

        output: dict[str, Any] | None | Unset
        if isinstance(self.output, Unset):
            output = UNSET
        elif isinstance(self.output, SpecialistOutputProjection):
            output = self.output.to_dict()
        else:
            output = self.output

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "floor": floor,
                "name": name,
            }
        )
        if output is not UNSET:
            field_dict["output"] = output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.specialist_output_projection import (
            SpecialistOutputProjection,  # noqa: PLC0415
        )

        d = dict(src_dict)
        files = cast(list[str], d.pop("files"))

        floor = d.pop("floor")

        name = d.pop("name")

        def _parse_output(data: object) -> None | SpecialistOutputProjection | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_type_0 = SpecialistOutputProjection.from_dict(data)

                return output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SpecialistOutputProjection | Unset, data)

        output = _parse_output(d.pop("output", UNSET))

        specialist_pass_execution = cls(
            files=files,
            floor=floor,
            name=name,
            output=output,
        )

        specialist_pass_execution.additional_properties = d
        return specialist_pass_execution

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
