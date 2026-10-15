from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerFindingValidation")


@_attrs_define
class CustomerFindingValidation:
    """
    Attributes:
        recorded_at (datetime.datetime): When Proofline recorded the decision.
        source (str): Where the decision came from: `UI` for the app's assessment controls,
             `GITHUB_COMMENT` for a pull request comment, or `PROOFLINE` for the
             automatic `ALREADY_COVERED` decision.
        validation (str): The decision: `CONFIRMED`, `DISMISSED`, `FIXED`, `ACCEPTED_RISK` or
             `ALREADY_COVERED`.
        actor_github_user_id (int | None | Unset): The actor's stable GitHub user ID. Null for the automatic decision.
        actor_login (None | str | Unset): The actor's GitHub login, a display label to render as text. Null for
             the automatic decision.
        covering_author_kind (None | str | Unset): For `ALREADY_COVERED`, `HUMAN` or `BOT`. Null for every other
            decision.
        covering_author_login (None | str | Unset): For `ALREADY_COVERED`, the login of whoever wrote the covering
            comment,
             to render as text. Null for every other decision.
        covering_comment_created_at (datetime.datetime | None | Unset): For `ALREADY_COVERED`, when the covering comment
            was written. Null for
             every other decision.
        github_comment_url (None | str | Unset): The comment that carried a decision made on GitHub, or, for
             `ALREADY_COVERED`, the other reviewer's comment the decision rests on.
    """

    recorded_at: datetime.datetime
    source: str
    validation: str
    actor_github_user_id: int | None | Unset = UNSET
    actor_login: None | str | Unset = UNSET
    covering_author_kind: None | str | Unset = UNSET
    covering_author_login: None | str | Unset = UNSET
    covering_comment_created_at: datetime.datetime | None | Unset = UNSET
    github_comment_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        recorded_at = self.recorded_at.isoformat()

        source = self.source

        validation = self.validation

        actor_github_user_id: int | None | Unset
        if isinstance(self.actor_github_user_id, Unset):
            actor_github_user_id = UNSET
        else:
            actor_github_user_id = self.actor_github_user_id

        actor_login: None | str | Unset
        if isinstance(self.actor_login, Unset):
            actor_login = UNSET
        else:
            actor_login = self.actor_login

        covering_author_kind: None | str | Unset
        if isinstance(self.covering_author_kind, Unset):
            covering_author_kind = UNSET
        else:
            covering_author_kind = self.covering_author_kind

        covering_author_login: None | str | Unset
        if isinstance(self.covering_author_login, Unset):
            covering_author_login = UNSET
        else:
            covering_author_login = self.covering_author_login

        covering_comment_created_at: None | str | Unset
        if isinstance(self.covering_comment_created_at, Unset):
            covering_comment_created_at = UNSET
        elif isinstance(self.covering_comment_created_at, datetime.datetime):
            covering_comment_created_at = self.covering_comment_created_at.isoformat()
        else:
            covering_comment_created_at = self.covering_comment_created_at

        github_comment_url: None | str | Unset
        if isinstance(self.github_comment_url, Unset):
            github_comment_url = UNSET
        else:
            github_comment_url = self.github_comment_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "recorded_at": recorded_at,
                "source": source,
                "validation": validation,
            }
        )
        if actor_github_user_id is not UNSET:
            field_dict["actor_github_user_id"] = actor_github_user_id
        if actor_login is not UNSET:
            field_dict["actor_login"] = actor_login
        if covering_author_kind is not UNSET:
            field_dict["covering_author_kind"] = covering_author_kind
        if covering_author_login is not UNSET:
            field_dict["covering_author_login"] = covering_author_login
        if covering_comment_created_at is not UNSET:
            field_dict["covering_comment_created_at"] = covering_comment_created_at
        if github_comment_url is not UNSET:
            field_dict["github_comment_url"] = github_comment_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        recorded_at = datetime.datetime.fromisoformat(d.pop("recorded_at"))

        source = d.pop("source")

        validation = d.pop("validation")

        def _parse_actor_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        actor_github_user_id = _parse_actor_github_user_id(d.pop("actor_github_user_id", UNSET))

        def _parse_actor_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_login = _parse_actor_login(d.pop("actor_login", UNSET))

        def _parse_covering_author_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        covering_author_kind = _parse_covering_author_kind(d.pop("covering_author_kind", UNSET))

        def _parse_covering_author_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        covering_author_login = _parse_covering_author_login(d.pop("covering_author_login", UNSET))

        def _parse_covering_comment_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                covering_comment_created_at_type_0 = datetime.datetime.fromisoformat(data)

                return covering_comment_created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        covering_comment_created_at = _parse_covering_comment_created_at(
            d.pop("covering_comment_created_at", UNSET)
        )

        def _parse_github_comment_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        github_comment_url = _parse_github_comment_url(d.pop("github_comment_url", UNSET))

        customer_finding_validation = cls(
            recorded_at=recorded_at,
            source=source,
            validation=validation,
            actor_github_user_id=actor_github_user_id,
            actor_login=actor_login,
            covering_author_kind=covering_author_kind,
            covering_author_login=covering_author_login,
            covering_comment_created_at=covering_comment_created_at,
            github_comment_url=github_comment_url,
        )

        customer_finding_validation.additional_properties = d
        return customer_finding_validation

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
