from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.occurrence_capture import OccurrenceCapture
    from ..models.override import Override


T = TypeVar("T", bound="GateState")


@_attrs_define
class GateState:
    """
    Attributes:
        occurrence_captures (list[OccurrenceCapture]): The occurrence questions the gate's approval deferred, as each
             observed execution of its deployment answered them. Outcome-only
             records: none of them changes the gate or grades a prediction.
        status (str): Local gate state. ALLOWED/BLOCKED can precede provider delivery.
             This field does not confirm that GitHub released or blocked a run.
        override_record (None | Override | Unset): Recorded override authorization, not confirmation of provider
            delivery.
    """

    occurrence_captures: list[OccurrenceCapture]
    status: str
    override_record: None | Override | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.override import Override  # noqa: PLC0415

        occurrence_captures = []
        for occurrence_captures_item_data in self.occurrence_captures:
            occurrence_captures_item = occurrence_captures_item_data.to_dict()
            occurrence_captures.append(occurrence_captures_item)

        status = self.status

        override_record: dict[str, Any] | None | Unset
        if isinstance(self.override_record, Unset):
            override_record = UNSET
        elif isinstance(self.override_record, Override):
            override_record = self.override_record.to_dict()
        else:
            override_record = self.override_record

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "occurrence_captures": occurrence_captures,
                "status": status,
            }
        )
        if override_record is not UNSET:
            field_dict["override_record"] = override_record

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.occurrence_capture import OccurrenceCapture  # noqa: PLC0415
        from ..models.override import Override  # noqa: PLC0415

        d = dict(src_dict)
        occurrence_captures = []
        _occurrence_captures = d.pop("occurrence_captures")
        for occurrence_captures_item_data in _occurrence_captures:
            occurrence_captures_item = OccurrenceCapture.from_dict(occurrence_captures_item_data)

            occurrence_captures.append(occurrence_captures_item)

        status = d.pop("status")

        def _parse_override_record(data: object) -> None | Override | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                override_record_type_0 = Override.from_dict(data)

                return override_record_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Override | Unset, data)

        override_record = _parse_override_record(d.pop("override_record", UNSET))

        gate_state = cls(
            occurrence_captures=occurrence_captures,
            status=status,
            override_record=override_record,
        )

        gate_state.additional_properties = d
        return gate_state

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
