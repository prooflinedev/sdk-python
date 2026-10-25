from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CoverageUploadResponse")


@_attrs_define
class CoverageUploadResponse:
    """The report the upload recorded, or the one an identical upload recorded.

    Attributes:
        covered_lines (int): Covered lines among those instrumented lines.
        created (bool): False when the same reports for this commit were already recorded.
        formats (list[str]): The format of each report, in upload order.
        instrumented_lines (int): Instrumented lines across the reports, a file two reports name under
             one path counted once.
        report_id (UUID): The recorded report.
        tested_sha (str): The commit the reports tested, as the upload named it.
    """

    covered_lines: int
    created: bool
    formats: list[str]
    instrumented_lines: int
    report_id: UUID
    tested_sha: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        covered_lines = self.covered_lines

        created = self.created

        formats = self.formats

        instrumented_lines = self.instrumented_lines

        report_id = str(self.report_id)

        tested_sha = self.tested_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "covered_lines": covered_lines,
                "created": created,
                "formats": formats,
                "instrumented_lines": instrumented_lines,
                "report_id": report_id,
                "tested_sha": tested_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        covered_lines = d.pop("covered_lines")

        created = d.pop("created")

        formats = cast(list[str], d.pop("formats"))

        instrumented_lines = d.pop("instrumented_lines")

        report_id = UUID(d.pop("report_id"))

        tested_sha = d.pop("tested_sha")

        coverage_upload_response = cls(
            covered_lines=covered_lines,
            created=created,
            formats=formats,
            instrumented_lines=instrumented_lines,
            report_id=report_id,
            tested_sha=tested_sha,
        )

        coverage_upload_response.additional_properties = d
        return coverage_upload_response

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
