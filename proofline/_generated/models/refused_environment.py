from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RefusedEnvironment")


@_attrs_define
class RefusedEnvironment:
    """An environment a refusal names. `external_key` is how its pages are
    addressed.

       Attributes:
           display_name (str): The environment's display name. Tenant free text: render as text.
           external_key (str): The environment's stable machine key, unique within the organization.
           id (UUID): The environment's identifier.
           status (str): The environment's lifecycle status, such as `READY`.
    """

    display_name: str
    external_key: str
    id: UUID
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        external_key = self.external_key

        id = str(self.id)

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "external_key": external_key,
                "id": id,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        external_key = d.pop("external_key")

        id = UUID(d.pop("id"))

        status = d.pop("status")

        refused_environment = cls(
            display_name=display_name,
            external_key=external_key,
            id=id,
            status=status,
        )

        refused_environment.additional_properties = d
        return refused_environment

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
