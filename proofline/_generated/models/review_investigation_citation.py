from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewInvestigationCitation")


@_attrs_define
class ReviewInvestigationCitation:
    """One environment evidence record a finding cites, as Proofline verified
    it.

       Attributes:
           collection_id (UUID): The evidence collection that holds the record.
           digest (str): The record's stored digest.
           record_id (UUID): The record's ID.
           table (str): The table that holds the record.
    """

    collection_id: UUID
    digest: str
    record_id: UUID
    table: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        collection_id = str(self.collection_id)

        digest = self.digest

        record_id = str(self.record_id)

        table = self.table

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "collection_id": collection_id,
                "digest": digest,
                "record_id": record_id,
                "table": table,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        collection_id = UUID(d.pop("collection_id"))

        digest = d.pop("digest")

        record_id = UUID(d.pop("record_id"))

        table = d.pop("table")

        review_investigation_citation = cls(
            collection_id=collection_id,
            digest=digest,
            record_id=record_id,
            table=table,
        )

        review_investigation_citation.additional_properties = d
        return review_investigation_citation

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
