from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.specialist_assessment_execution import SpecialistAssessmentExecution


T = TypeVar("T", bound="SpecialistExecutionView")


@_attrs_define
class SpecialistExecutionView:
    """
    Attributes:
        assessments (list[SpecialistAssessmentExecution]): The applied specialist roster per exact assessment execution.
        selection_recorded (bool): False until the applied parent captures its specialist choices.
    """

    assessments: list[SpecialistAssessmentExecution]
    selection_recorded: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessments = []
        for assessments_item_data in self.assessments:
            assessments_item = assessments_item_data.to_dict()
            assessments.append(assessments_item)

        selection_recorded = self.selection_recorded

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessments": assessments,
                "selection_recorded": selection_recorded,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.specialist_assessment_execution import (
            SpecialistAssessmentExecution,  # noqa: PLC0415
        )

        d = dict(src_dict)
        assessments = []
        _assessments = d.pop("assessments")
        for assessments_item_data in _assessments:
            assessments_item = SpecialistAssessmentExecution.from_dict(assessments_item_data)

            assessments.append(assessments_item)

        selection_recorded = d.pop("selection_recorded")

        specialist_execution_view = cls(
            assessments=assessments,
            selection_recorded=selection_recorded,
        )

        specialist_execution_view.additional_properties = d
        return specialist_execution_view

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
