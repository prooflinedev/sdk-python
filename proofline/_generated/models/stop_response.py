from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.actor_view import ActorView


T = TypeVar("T", bound="StopResponse")


@_attrs_define
class StopResponse:
    """What stopping a review recorded.

    Attributes:
        review_id (UUID): Identifier of the stopped review.
        status (str): Always `STOPPED`: the review's status once the stop is committed.
        stopped_at (datetime.datetime): Time when the review was stopped.
        stopped_by (ActorView): The person behind an action on a review, as the page names them.
    """

    review_id: UUID
    status: str
    stopped_at: datetime.datetime
    stopped_by: ActorView
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        review_id = str(self.review_id)

        status = self.status

        stopped_at = self.stopped_at.isoformat()

        stopped_by = self.stopped_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "review_id": review_id,
                "status": status,
                "stopped_at": stopped_at,
                "stopped_by": stopped_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actor_view import ActorView  # noqa: PLC0415

        d = dict(src_dict)
        review_id = UUID(d.pop("review_id"))

        status = d.pop("status")

        stopped_at = datetime.datetime.fromisoformat(d.pop("stopped_at"))

        stopped_by = ActorView.from_dict(d.pop("stopped_by"))

        stop_response = cls(
            review_id=review_id,
            status=status,
            stopped_at=stopped_at,
            stopped_by=stopped_by,
        )

        stop_response.additional_properties = d
        return stop_response

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
