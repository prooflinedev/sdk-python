from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pass_projection import PassProjection


T = TypeVar("T", bound="AssessmentProjection")


@_attrs_define
class AssessmentProjection:
    """
    Attributes:
        assessment_id (UUID): Assessment that owns this route binding.
        environment_id (UUID): Environment that the assessment covers.
        pass_output_recorded (bool): Whether this assessment retained a generalist output record.
        passes (list[PassProjection]): Pass and symbolic model binding retained by the plan.
        reach (str): Environment reach retained by the plan.
        pass_output_sha256 (None | str | Unset): Digest of the immutable generalist output, when the assessment retained
            one.
    """

    assessment_id: UUID
    environment_id: UUID
    pass_output_recorded: bool
    passes: list[PassProjection]
    reach: str
    pass_output_sha256: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_id = str(self.assessment_id)

        environment_id = str(self.environment_id)

        pass_output_recorded = self.pass_output_recorded

        passes = []
        for passes_item_data in self.passes:
            passes_item = passes_item_data.to_dict()
            passes.append(passes_item)

        reach = self.reach

        pass_output_sha256: None | str | Unset
        if isinstance(self.pass_output_sha256, Unset):
            pass_output_sha256 = UNSET
        else:
            pass_output_sha256 = self.pass_output_sha256

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_id": assessment_id,
                "environment_id": environment_id,
                "pass_output_recorded": pass_output_recorded,
                "passes": passes,
                "reach": reach,
            }
        )
        if pass_output_sha256 is not UNSET:
            field_dict["pass_output_sha256"] = pass_output_sha256

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pass_projection import PassProjection  # noqa: PLC0415

        d = dict(src_dict)
        assessment_id = UUID(d.pop("assessment_id"))

        environment_id = UUID(d.pop("environment_id"))

        pass_output_recorded = d.pop("pass_output_recorded")

        passes = []
        _passes = d.pop("passes")
        for passes_item_data in _passes:
            passes_item = PassProjection.from_dict(passes_item_data)

            passes.append(passes_item)

        reach = d.pop("reach")

        def _parse_pass_output_sha256(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pass_output_sha256 = _parse_pass_output_sha256(d.pop("pass_output_sha256", UNSET))

        assessment_projection = cls(
            assessment_id=assessment_id,
            environment_id=environment_id,
            pass_output_recorded=pass_output_recorded,
            passes=passes,
            reach=reach,
            pass_output_sha256=pass_output_sha256,
        )

        assessment_projection.additional_properties = d
        return assessment_projection

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
