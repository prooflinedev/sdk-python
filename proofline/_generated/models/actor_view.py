from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ActorView")


@_attrs_define
class ActorView:
    """The person behind an action on a review, as the page names them.

    Attributes:
        github_user_id (int): Stable GitHub identity. The login below is display metadata.
        login (str): The login they were known by when they acted. Display metadata.
        profile_url (None | str | Unset): Their profile on the deployment's GitHub host.
    """

    github_user_id: int
    login: str
    profile_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        github_user_id = self.github_user_id

        login = self.login

        profile_url: None | str | Unset
        if isinstance(self.profile_url, Unset):
            profile_url = UNSET
        else:
            profile_url = self.profile_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "github_user_id": github_user_id,
                "login": login,
            }
        )
        if profile_url is not UNSET:
            field_dict["profile_url"] = profile_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        github_user_id = d.pop("github_user_id")

        login = d.pop("login")

        def _parse_profile_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_url = _parse_profile_url(d.pop("profile_url", UNSET))

        actor_view = cls(
            github_user_id=github_user_id,
            login=login,
            profile_url=profile_url,
        )

        actor_view.additional_properties = d
        return actor_view

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
