from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.reach_step_view import ReachStepView


T = TypeVar("T", bound="ReachedEntityView")


@_attrs_define
class ReachedEntityView:
    """
    Attributes:
        entity_id (UUID): World's entity ID.
        kind (str): The entity's kind, such as `service` or `queue`.
        label (str): World's display label for the entity: environment evidence for
             readers of this organization, never published to GitHub.
        path (list[ReachStepView]): The recorded relation assertions from the deployed root to the entity.
        type_keys (list[str]): World's registry type keys for the entity.
    """

    entity_id: UUID
    kind: str
    label: str
    path: list[ReachStepView]
    type_keys: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_id = str(self.entity_id)

        kind = self.kind

        label = self.label

        path = []
        for path_item_data in self.path:
            path_item = path_item_data.to_dict()
            path.append(path_item)

        type_keys = self.type_keys

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_id": entity_id,
                "kind": kind,
                "label": label,
                "path": path,
                "type_keys": type_keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reach_step_view import ReachStepView  # noqa: PLC0415

        d = dict(src_dict)
        entity_id = UUID(d.pop("entity_id"))

        kind = d.pop("kind")

        label = d.pop("label")

        path = []
        _path = d.pop("path")
        for path_item_data in _path:
            path_item = ReachStepView.from_dict(path_item_data)

            path.append(path_item)

        type_keys = cast(list[str], d.pop("type_keys"))

        reached_entity_view = cls(
            entity_id=entity_id,
            kind=kind,
            label=label,
            path=path,
            type_keys=type_keys,
        )

        reached_entity_view.additional_properties = d
        return reached_entity_view

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
