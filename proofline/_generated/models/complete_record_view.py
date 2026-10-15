from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CompleteRecordView")


@_attrs_define
class CompleteRecordView:
    """World's immutable record of the complete answer an omitted list comes
    from.

       Attributes:
           attribution_digest (str): The `sha256:` digest of the complete attribution in that record.
           world_evaluation_id (str): The evaluation World recorded, which holds every condition.
    """

    attribution_digest: str
    world_evaluation_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attribution_digest = self.attribution_digest

        world_evaluation_id = self.world_evaluation_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attribution_digest": attribution_digest,
                "world_evaluation_id": world_evaluation_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attribution_digest = d.pop("attribution_digest")

        world_evaluation_id = d.pop("world_evaluation_id")

        complete_record_view = cls(
            attribution_digest=attribution_digest,
            world_evaluation_id=world_evaluation_id,
        )

        complete_record_view.additional_properties = d
        return complete_record_view

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
