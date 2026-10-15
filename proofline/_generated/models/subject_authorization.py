from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SubjectAuthorization")


@_attrs_define
class SubjectAuthorization:
    """One assessment's authorization of one subject, by identity.

    The display name is not the answer on its own: an environment's external key
    is unique within its organization and a display name is mutable metadata,
    so two environments of one review can carry the same one.
    Collapsing to it would leave a reader unable to tell which assessment
    authorized the subject and which one gapped, which is the confusion this
    field exists to remove.

       Attributes:
           assessment_id (UUID): The assessment this authorization belongs to, as `AssessmentView.id`
                names it. A reader joins on this, never on the display name.
           environment_display_name (str): What a reader recognizes the environment by. Display metadata, and
                tenant free text: a consumer contains it before rendering.
           environment_external_key (str): The environment's stable machine key, unique within the organization.
           environment_id (UUID): The environment the authorizing assessment belongs to.
    """

    assessment_id: UUID
    environment_display_name: str
    environment_external_key: str
    environment_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_id = str(self.assessment_id)

        environment_display_name = self.environment_display_name

        environment_external_key = self.environment_external_key

        environment_id = str(self.environment_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_id": assessment_id,
                "environment_display_name": environment_display_name,
                "environment_external_key": environment_external_key,
                "environment_id": environment_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assessment_id = UUID(d.pop("assessment_id"))

        environment_display_name = d.pop("environment_display_name")

        environment_external_key = d.pop("environment_external_key")

        environment_id = UUID(d.pop("environment_id"))

        subject_authorization = cls(
            assessment_id=assessment_id,
            environment_display_name=environment_display_name,
            environment_external_key=environment_external_key,
            environment_id=environment_id,
        )

        subject_authorization.additional_properties = d
        return subject_authorization

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
