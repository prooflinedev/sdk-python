from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.review_investigation_citation import ReviewInvestigationCitation


T = TypeVar("T", bound="ReviewInvestigationFinding")


@_attrs_define
class ReviewInvestigationFinding:
    """One supported finding of an environment investigation.

    Attributes:
        area (str): What the finding is about: `secrets`, `configuration`, `iam`,
             `network`, `capacity` or `other`.
        assessment_id (UUID): The environment assessment whose investigation recorded the finding.
        citations (list[ReviewInvestigationCitation]): The evidence records the finding cites, each verified, in the
            order
             the finding cites them.
        detail (str): Model text with protected values withheld. Render it as plain text.
        title (str): Model text with protected values withheld. Render it as plain text.
    """

    area: str
    assessment_id: UUID
    citations: list[ReviewInvestigationCitation]
    detail: str
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area = self.area

        assessment_id = str(self.assessment_id)

        citations = []
        for citations_item_data in self.citations:
            citations_item = citations_item_data.to_dict()
            citations.append(citations_item)

        detail = self.detail

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area": area,
                "assessment_id": assessment_id,
                "citations": citations,
                "detail": detail,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_investigation_citation import ReviewInvestigationCitation  # noqa: PLC0415

        d = dict(src_dict)
        area = d.pop("area")

        assessment_id = UUID(d.pop("assessment_id"))

        citations = []
        _citations = d.pop("citations")
        for citations_item_data in _citations:
            citations_item = ReviewInvestigationCitation.from_dict(citations_item_data)

            citations.append(citations_item)

        detail = d.pop("detail")

        title = d.pop("title")

        review_investigation_finding = cls(
            area=area,
            assessment_id=assessment_id,
            citations=citations,
            detail=detail,
            title=title,
        )

        review_investigation_finding.additional_properties = d
        return review_investigation_finding

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
