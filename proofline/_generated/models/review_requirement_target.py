from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewRequirementTarget")


@_attrs_define
class ReviewRequirementTarget:
    """The delivery target whose confirmed entry a finding reports, as its Gate
    requirements page addresses it.

       Attributes:
           delivery_target_id (UUID): The delivery target.
           environment_id (UUID): The environment of the assessment that asked the requirement.
           repository_full_name (str): The repository's `owner/name`, which names the target to a reader.
           repository_name (str): The repository's name, as the page's address names it.
    """

    delivery_target_id: UUID
    environment_id: UUID
    repository_full_name: str
    repository_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        delivery_target_id = str(self.delivery_target_id)

        environment_id = str(self.environment_id)

        repository_full_name = self.repository_full_name

        repository_name = self.repository_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "delivery_target_id": delivery_target_id,
                "environment_id": environment_id,
                "repository_full_name": repository_full_name,
                "repository_name": repository_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        delivery_target_id = UUID(d.pop("delivery_target_id"))

        environment_id = UUID(d.pop("environment_id"))

        repository_full_name = d.pop("repository_full_name")

        repository_name = d.pop("repository_name")

        review_requirement_target = cls(
            delivery_target_id=delivery_target_id,
            environment_id=environment_id,
            repository_full_name=repository_full_name,
            repository_name=repository_name,
        )

        review_requirement_target.additional_properties = d
        return review_requirement_target

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
