from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="UploadedReport")


@_attrs_define
class UploadedReport:
    """
    Attributes:
        content (str): The report text, exactly as the coverage tool wrote it.
        name (str): A relative name for the report, such as `web/lcov.info`, unique in
             the upload.
    """

    content: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "content": content,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        content = d.pop("content")

        name = d.pop("name")

        uploaded_report = cls(
            content=content,
            name=name,
        )

        return uploaded_report
