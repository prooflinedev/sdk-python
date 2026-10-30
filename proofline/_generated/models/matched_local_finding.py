from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MatchedLocalFinding")


@_attrs_define
class MatchedLocalFinding:
    """A local occurrence with the same semantic fingerprint as this finding.

    Attributes:
        created_at (datetime.datetime): When the local review was requested.
        finding_id (UUID): The occurrence in that local review.
        review_id (UUID): The author's local review, linked by exact patch identity.
    """

    created_at: datetime.datetime
    finding_id: UUID
    review_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        finding_id = str(self.finding_id)

        review_id = str(self.review_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "finding_id": finding_id,
                "review_id": review_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        finding_id = UUID(d.pop("finding_id"))

        review_id = UUID(d.pop("review_id"))

        matched_local_finding = cls(
            created_at=created_at,
            finding_id=finding_id,
            review_id=review_id,
        )

        matched_local_finding.additional_properties = d
        return matched_local_finding

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
