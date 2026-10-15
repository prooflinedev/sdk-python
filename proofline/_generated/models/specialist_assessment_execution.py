from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.specialist_pass_execution import SpecialistPassExecution


T = TypeVar("T", bound="SpecialistAssessmentExecution")


@_attrs_define
class SpecialistAssessmentExecution:
    """
    Attributes:
        assessment_id (UUID): The immutable assessment whose specialist execution is reported.
        passes (list[SpecialistPassExecution]): Selected specialist passes and their retained execution outputs.
    """

    assessment_id: UUID
    passes: list[SpecialistPassExecution]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_id = str(self.assessment_id)

        passes = []
        for passes_item_data in self.passes:
            passes_item = passes_item_data.to_dict()
            passes.append(passes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_id": assessment_id,
                "passes": passes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.specialist_pass_execution import SpecialistPassExecution  # noqa: PLC0415

        d = dict(src_dict)
        assessment_id = UUID(d.pop("assessment_id"))

        passes = []
        _passes = d.pop("passes")
        for passes_item_data in _passes:
            passes_item = SpecialistPassExecution.from_dict(passes_item_data)

            passes.append(passes_item)

        specialist_assessment_execution = cls(
            assessment_id=assessment_id,
            passes=passes,
        )

        specialist_assessment_execution.additional_properties = d
        return specialist_assessment_execution

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
