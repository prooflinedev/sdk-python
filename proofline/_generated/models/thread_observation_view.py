from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.thread_observation_freshness import ThreadObservationFreshness
from ..models.thread_provider_state import ThreadProviderState
from ..models.thread_reply_evidence import ThreadReplyEvidence
from ..types import UNSET, Unset

T = TypeVar("T", bound="ThreadObservationView")


@_attrs_define
class ThreadObservationView:
    """A read of GitHub's thread state. `observed_at` is when Proofline read it.

    Attributes:
        freshness (ThreadObservationFreshness):
        observed_at (datetime.datetime): When Proofline read the thread state from GitHub.
        reply_evidence (ThreadReplyEvidence):
        github_comment_url (None | str | Unset): The finding's root comment on GitHub. Absent when the repository is
            unknown.
        provider_state (None | ThreadProviderState | Unset): Absent only when the provider read failed before GitHub
            returned state.
        resolver_github_user_id (int | None | Unset): The stable GitHub identity of whoever resolved the thread. Absent
            when GitHub named no resolver.
        resolver_login (None | str | Unset): The login of whoever resolved the thread, as GitHub reported it. Provider
            text, and absent when GitHub named no resolver.
    """

    freshness: ThreadObservationFreshness
    observed_at: datetime.datetime
    reply_evidence: ThreadReplyEvidence
    github_comment_url: None | str | Unset = UNSET
    provider_state: None | ThreadProviderState | Unset = UNSET
    resolver_github_user_id: int | None | Unset = UNSET
    resolver_login: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        freshness = self.freshness.value

        observed_at = self.observed_at.isoformat()

        reply_evidence = self.reply_evidence.value

        github_comment_url: None | str | Unset
        if isinstance(self.github_comment_url, Unset):
            github_comment_url = UNSET
        else:
            github_comment_url = self.github_comment_url

        provider_state: None | str | Unset
        if isinstance(self.provider_state, Unset):
            provider_state = UNSET
        elif isinstance(self.provider_state, ThreadProviderState):
            provider_state = self.provider_state.value
        else:
            provider_state = self.provider_state

        resolver_github_user_id: int | None | Unset
        if isinstance(self.resolver_github_user_id, Unset):
            resolver_github_user_id = UNSET
        else:
            resolver_github_user_id = self.resolver_github_user_id

        resolver_login: None | str | Unset
        if isinstance(self.resolver_login, Unset):
            resolver_login = UNSET
        else:
            resolver_login = self.resolver_login

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "freshness": freshness,
                "observed_at": observed_at,
                "reply_evidence": reply_evidence,
            }
        )
        if github_comment_url is not UNSET:
            field_dict["github_comment_url"] = github_comment_url
        if provider_state is not UNSET:
            field_dict["provider_state"] = provider_state
        if resolver_github_user_id is not UNSET:
            field_dict["resolver_github_user_id"] = resolver_github_user_id
        if resolver_login is not UNSET:
            field_dict["resolver_login"] = resolver_login

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        freshness = ThreadObservationFreshness(d.pop("freshness"))

        observed_at = datetime.datetime.fromisoformat(d.pop("observed_at"))

        reply_evidence = ThreadReplyEvidence(d.pop("reply_evidence"))

        def _parse_github_comment_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        github_comment_url = _parse_github_comment_url(d.pop("github_comment_url", UNSET))

        def _parse_provider_state(data: object) -> None | ThreadProviderState | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                provider_state_type_0 = ThreadProviderState(data)

                return provider_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ThreadProviderState | Unset, data)

        provider_state = _parse_provider_state(d.pop("provider_state", UNSET))

        def _parse_resolver_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        resolver_github_user_id = _parse_resolver_github_user_id(
            d.pop("resolver_github_user_id", UNSET)
        )

        def _parse_resolver_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolver_login = _parse_resolver_login(d.pop("resolver_login", UNSET))

        thread_observation_view = cls(
            freshness=freshness,
            observed_at=observed_at,
            reply_evidence=reply_evidence,
            github_comment_url=github_comment_url,
            provider_state=provider_state,
            resolver_github_user_id=resolver_github_user_id,
            resolver_login=resolver_login,
        )

        thread_observation_view.additional_properties = d
        return thread_observation_view

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
