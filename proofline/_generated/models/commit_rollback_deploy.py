from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommitRollbackDeploy")


@_attrs_define
class CommitRollbackDeploy:
    """One deploy a rollback names.

    Attributes:
        commit_sha (str): The commit that deploy ran.
        landed_at (datetime.datetime): When its last deployment first succeeded, or its AWS run ended.
        deploy_url (None | str | Unset): The deploy's console page.
    """

    commit_sha: str
    landed_at: datetime.datetime
    deploy_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        commit_sha = self.commit_sha

        landed_at = self.landed_at.isoformat()

        deploy_url: None | str | Unset
        if isinstance(self.deploy_url, Unset):
            deploy_url = UNSET
        else:
            deploy_url = self.deploy_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "commit_sha": commit_sha,
                "landed_at": landed_at,
            }
        )
        if deploy_url is not UNSET:
            field_dict["deploy_url"] = deploy_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        commit_sha = d.pop("commit_sha")

        landed_at = datetime.datetime.fromisoformat(d.pop("landed_at"))

        def _parse_deploy_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deploy_url = _parse_deploy_url(d.pop("deploy_url", UNSET))

        commit_rollback_deploy = cls(
            commit_sha=commit_sha,
            landed_at=landed_at,
            deploy_url=deploy_url,
        )

        commit_rollback_deploy.additional_properties = d
        return commit_rollback_deploy

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
