from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScanResponse")


@_attrs_define
class ScanResponse:
    """What a scan request resolved to.

    Attributes:
        outcome (str): `CREATED`, `EXISTING` when this request id was already resolved, or
             `REPOSITORY_UNAVAILABLE` when GitHub could not resolve it.
        resolution_id (UUID): The request's one resolution receipt.
        review_id (None | Unset | UUID): The scan review, readable through the review routes. Absent when
             GitHub could not resolve the request.
    """

    outcome: str
    resolution_id: UUID
    review_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        outcome = self.outcome

        resolution_id = str(self.resolution_id)

        review_id: None | str | Unset
        if isinstance(self.review_id, Unset):
            review_id = UNSET
        elif isinstance(self.review_id, UUID):
            review_id = str(self.review_id)
        else:
            review_id = self.review_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "outcome": outcome,
                "resolution_id": resolution_id,
            }
        )
        if review_id is not UNSET:
            field_dict["review_id"] = review_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        outcome = d.pop("outcome")

        resolution_id = UUID(d.pop("resolution_id"))

        def _parse_review_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                review_id_type_0 = UUID(data)

                return review_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        review_id = _parse_review_id(d.pop("review_id", UNSET))

        scan_response = cls(
            outcome=outcome,
            resolution_id=resolution_id,
            review_id=review_id,
        )

        scan_response.additional_properties = d
        return scan_response

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
