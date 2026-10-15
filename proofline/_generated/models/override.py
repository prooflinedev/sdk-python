from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Override")


@_attrs_define
class Override:
    """
    Attributes:
        github_environment_id (int): The GitHub environment ID the approval applied to.
        github_user_id (int): The GitHub user ID of the person whose GitHub deployment approval
             overrode the gate.
        github_user_login (str): That person's GitHub login as recorded with the approval, a display
             label truncated past 128 characters.
        comment (None | str | Unset): The comment recorded with the approval, truncated past 8000
             characters.
    """

    github_environment_id: int
    github_user_id: int
    github_user_login: str
    comment: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        github_environment_id = self.github_environment_id

        github_user_id = self.github_user_id

        github_user_login = self.github_user_login

        comment: None | str | Unset
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "github_environment_id": github_environment_id,
                "github_user_id": github_user_id,
                "github_user_login": github_user_login,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        github_environment_id = d.pop("github_environment_id")

        github_user_id = d.pop("github_user_id")

        github_user_login = d.pop("github_user_login")

        def _parse_comment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        comment = _parse_comment(d.pop("comment", UNSET))

        override = cls(
            github_environment_id=github_environment_id,
            github_user_id=github_user_id,
            github_user_login=github_user_login,
            comment=comment,
        )

        override.additional_properties = d
        return override

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
