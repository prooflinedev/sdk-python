from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.commit_deploy import CommitDeploy


T = TypeVar("T", bound="CommitDeployVerifications")


@_attrs_define
class CommitDeployVerifications:
    """The deploys of one commit that Proofline recorded, across the
    organization's environments.

       Attributes:
           deploys (list[CommitDeploy]): Each recorded deploy, earliest landing first.
           recorded (bool): Whether the ledger holds any deploy of the commit. `false` says only
                that none was recorded, never anything about a deploy.
    """

    deploys: list[CommitDeploy]
    recorded: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deploys = []
        for deploys_item_data in self.deploys:
            deploys_item = deploys_item_data.to_dict()
            deploys.append(deploys_item)

        recorded = self.recorded

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deploys": deploys,
                "recorded": recorded,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commit_deploy import CommitDeploy  # noqa: PLC0415

        d = dict(src_dict)
        deploys = []
        _deploys = d.pop("deploys")
        for deploys_item_data in _deploys:
            deploys_item = CommitDeploy.from_dict(deploys_item_data)

            deploys.append(deploys_item)

        recorded = d.pop("recorded")

        commit_deploy_verifications = cls(
            deploys=deploys,
            recorded=recorded,
        )

        commit_deploy_verifications.additional_properties = d
        return commit_deploy_verifications

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
