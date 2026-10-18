from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReachStepView")


@_attrs_define
class ReachStepView:
    """
    Attributes:
        assertion_id (UUID): The World relation assertion behind this step.
        direction (str): `OUT` when the step follows the relation from its subject, `IN` when
             it follows it back to the subject.
        relation (str): The relation key, such as `proofline.relation.consumes_api`.
    """

    assertion_id: UUID
    direction: str
    relation: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assertion_id = str(self.assertion_id)

        direction = self.direction

        relation = self.relation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assertion_id": assertion_id,
                "direction": direction,
                "relation": relation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assertion_id = UUID(d.pop("assertion_id"))

        direction = d.pop("direction")

        relation = d.pop("relation")

        reach_step_view = cls(
            assertion_id=assertion_id,
            direction=direction,
            relation=relation,
        )

        reach_step_view.additional_properties = d
        return reach_step_view

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
