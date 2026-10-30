from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EarlierOpenFinding")


@_attrs_define
class EarlierOpenFinding:
    """A published occurrence of an unresolved series absent from the current run.

    Attributes:
        finding_id (UUID): The occurrence in the series' first published review.
        finding_series_id (UUID): The unresolved environment finding series counted for this run.
        review_id (UUID): The first published review containing this occurrence.
        run_number (int): The earlier pull-request run that contains this occurrence.
        severity (str): Severity used by the series count; the linked occurrence may be less severe.
    """

    finding_id: UUID
    finding_series_id: UUID
    review_id: UUID
    run_number: int
    severity: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        finding_id = str(self.finding_id)

        finding_series_id = str(self.finding_series_id)

        review_id = str(self.review_id)

        run_number = self.run_number

        severity = self.severity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "finding_id": finding_id,
                "finding_series_id": finding_series_id,
                "review_id": review_id,
                "run_number": run_number,
                "severity": severity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        finding_id = UUID(d.pop("finding_id"))

        finding_series_id = UUID(d.pop("finding_series_id"))

        review_id = UUID(d.pop("review_id"))

        run_number = d.pop("run_number")

        severity = d.pop("severity")

        earlier_open_finding = cls(
            finding_id=finding_id,
            finding_series_id=finding_series_id,
            review_id=review_id,
            run_number=run_number,
            severity=severity,
        )

        earlier_open_finding.additional_properties = d
        return earlier_open_finding

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
