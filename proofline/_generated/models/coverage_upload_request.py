from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.uploaded_report import UploadedReport


T = TypeVar("T", bound="CoverageUploadRequest")


@_attrs_define
class CoverageUploadRequest:
    """The coverage reports a CI run produced for one commit.

    Attributes:
        reports (list[UploadedReport]): One to 50 reports, each LCOV, Cobertura XML, `JaCoCo` XML or a Go
             cover profile, in a JSON body of at most 64 MiB.
        tested_sha (str): The full 40-character commit the tests ran on. GitHub must have it in
             this repository. A merge commit counts for a pull request head that is
             one of its two parents.
    """

    reports: list[UploadedReport]
    tested_sha: str

    def to_dict(self) -> dict[str, Any]:
        reports = []
        for reports_item_data in self.reports:
            reports_item = reports_item_data.to_dict()
            reports.append(reports_item)

        tested_sha = self.tested_sha

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "reports": reports,
                "tested_sha": tested_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.uploaded_report import UploadedReport  # noqa: PLC0415

        d = dict(src_dict)
        reports = []
        _reports = d.pop("reports")
        for reports_item_data in _reports:
            reports_item = UploadedReport.from_dict(reports_item_data)

            reports.append(reports_item)

        tested_sha = d.pop("tested_sha")

        coverage_upload_request = cls(
            reports=reports,
            tested_sha=tested_sha,
        )

        return coverage_upload_request
