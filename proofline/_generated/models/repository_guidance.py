from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepositoryGuidance")


@_attrs_define
class RepositoryGuidance:
    """
    Attributes:
        repository_id (UUID): The repository's stable Proofline ID.
        additional_prompt (None | str | Unset): The repository-specific reviewer guidance new reviews snapshot, null
            when none is set.
    """

    repository_id: UUID
    additional_prompt: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_id = str(self.repository_id)

        additional_prompt: None | str | Unset
        if isinstance(self.additional_prompt, Unset):
            additional_prompt = UNSET
        else:
            additional_prompt = self.additional_prompt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository_id": repository_id,
            }
        )
        if additional_prompt is not UNSET:
            field_dict["additional_prompt"] = additional_prompt

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository_id = UUID(d.pop("repository_id"))

        def _parse_additional_prompt(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        additional_prompt = _parse_additional_prompt(d.pop("additional_prompt", UNSET))

        repository_guidance = cls(
            repository_id=repository_id,
            additional_prompt=additional_prompt,
        )

        repository_guidance.additional_properties = d
        return repository_guidance

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
