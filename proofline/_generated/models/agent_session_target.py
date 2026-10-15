from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AgentSessionTarget")


@_attrs_define
class AgentSessionTarget:
    """What a session is pinned to: the finding's own reviewed pull request.

    Attributes:
        github_repository_id (int): The repository's stable GitHub ID, which the connection allowlists.
        head_sha (str): The exact commit the review read. The session starts from it.
        pull_request_number (int): The reviewed pull request.
        repository_full_name (str): The repository's `owner/name` on GitHub, as last recorded.
        repository_id (UUID): The reviewed repository's Proofline ID.
    """

    github_repository_id: int
    head_sha: str
    pull_request_number: int
    repository_full_name: str
    repository_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        github_repository_id = self.github_repository_id

        head_sha = self.head_sha

        pull_request_number = self.pull_request_number

        repository_full_name = self.repository_full_name

        repository_id = str(self.repository_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "github_repository_id": github_repository_id,
                "head_sha": head_sha,
                "pull_request_number": pull_request_number,
                "repository_full_name": repository_full_name,
                "repository_id": repository_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        github_repository_id = d.pop("github_repository_id")

        head_sha = d.pop("head_sha")

        pull_request_number = d.pop("pull_request_number")

        repository_full_name = d.pop("repository_full_name")

        repository_id = UUID(d.pop("repository_id"))

        agent_session_target = cls(
            github_repository_id=github_repository_id,
            head_sha=head_sha,
            pull_request_number=pull_request_number,
            repository_full_name=repository_full_name,
            repository_id=repository_id,
        )

        agent_session_target.additional_properties = d
        return agent_session_target

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
