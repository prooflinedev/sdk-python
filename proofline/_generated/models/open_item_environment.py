from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.open_items_gap_reason import OpenItemsGapReason
from ..models.open_items_review_status import OpenItemsReviewStatus

T = TypeVar("T", bound="OpenItemEnvironment")


@_attrs_define
class OpenItemEnvironment:
    """
    Attributes:
        display_name (str): The environment's display name.
        environment_id (UUID): The environment whose assessment is not complete.
        reason (OpenItemsGapReason):
        status (OpenItemsReviewStatus):
    """

    display_name: str
    environment_id: UUID
    reason: OpenItemsGapReason
    status: OpenItemsReviewStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        environment_id = str(self.environment_id)

        reason = self.reason.value

        status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "display_name": display_name,
                "environment_id": environment_id,
                "reason": reason,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        display_name = d.pop("display_name")

        environment_id = UUID(d.pop("environment_id"))

        reason = OpenItemsGapReason(d.pop("reason"))

        status = OpenItemsReviewStatus(d.pop("status"))

        open_item_environment = cls(
            display_name=display_name,
            environment_id=environment_id,
            reason=reason,
            status=status,
        )

        open_item_environment.additional_properties = d
        return open_item_environment

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
