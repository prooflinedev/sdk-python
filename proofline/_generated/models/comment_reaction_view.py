from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.comment_reaction import CommentReaction
from ..types import UNSET, Unset

T = TypeVar("T", bound="CommentReactionView")


@_attrs_define
class CommentReactionView:
    """One stored reaction on the finding's root comment.

    Attributes:
        actor_github_user_id (int): The stable GitHub identity of whoever reacted.
        github_comment_id (int): The GitHub comment the reaction is on: the finding's root comment.
        reaction (CommentReaction):
        actor_login (None | str | Unset): Provider text. Render as text.
    """

    actor_github_user_id: int
    github_comment_id: int
    reaction: CommentReaction
    actor_login: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        actor_github_user_id = self.actor_github_user_id

        github_comment_id = self.github_comment_id

        reaction = self.reaction.value

        actor_login: None | str | Unset
        if isinstance(self.actor_login, Unset):
            actor_login = UNSET
        else:
            actor_login = self.actor_login

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actor_github_user_id": actor_github_user_id,
                "github_comment_id": github_comment_id,
                "reaction": reaction,
            }
        )
        if actor_login is not UNSET:
            field_dict["actor_login"] = actor_login

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        actor_github_user_id = d.pop("actor_github_user_id")

        github_comment_id = d.pop("github_comment_id")

        reaction = CommentReaction(d.pop("reaction"))

        def _parse_actor_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_login = _parse_actor_login(d.pop("actor_login", UNSET))

        comment_reaction_view = cls(
            actor_github_user_id=actor_github_user_id,
            github_comment_id=github_comment_id,
            reaction=reaction,
            actor_login=actor_login,
        )

        comment_reaction_view.additional_properties = d
        return comment_reaction_view

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
