from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CommitReviewResponse")


@_attrs_define
class CommitReviewResponse:
    """What a commit review request produced.

    Attributes:
        existing (bool): True when these exact commits already had a review and that one is
             returned. Sending the same commits twice reviews them once.
        review_id (UUID): The review of these commits, readable through the review and findings
             routes.
    """

    existing: bool
    review_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        existing = self.existing

        review_id = str(self.review_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "existing": existing,
                "review_id": review_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        existing = d.pop("existing")

        review_id = UUID(d.pop("review_id"))

        commit_review_response = cls(
            existing=existing,
            review_id=review_id,
        )

        commit_review_response.additional_properties = d
        return commit_review_response

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
