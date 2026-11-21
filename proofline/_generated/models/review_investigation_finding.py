from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.review_investigation_citation import ReviewInvestigationCitation
    from ..models.review_requirement_target import ReviewRequirementTarget


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
        requirement (None | ReviewRequirementTarget | Unset): The delivery target whose confirmed gate requirement the
            finding
             reports. Absent for an investigation's finding.
        source (Literal['CONFIRMED_REQUIREMENT'] | Literal['INVESTIGATION'] | None | Unset): What published the finding:
            a confirmed gate requirement its
             delivery target's services violate, or the environment investigation.
             Every listed finding carries it.
    """

    area: str
    assessment_id: UUID
    citations: list[ReviewInvestigationCitation]
    detail: str
    title: str
    requirement: None | ReviewRequirementTarget | Unset = UNSET
    source: Literal["CONFIRMED_REQUIREMENT"] | Literal["INVESTIGATION"] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.review_requirement_target import ReviewRequirementTarget  # noqa: PLC0415

        area = self.area

        assessment_id = str(self.assessment_id)

        citations = []
        for citations_item_data in self.citations:
            citations_item = citations_item_data.to_dict()
            citations.append(citations_item)

        detail = self.detail

        title = self.title

        requirement: dict[str, Any] | None | Unset
        if isinstance(self.requirement, Unset):
            requirement = UNSET
        elif isinstance(self.requirement, ReviewRequirementTarget):
            requirement = self.requirement.to_dict()
        else:
            requirement = self.requirement

        source: Literal["CONFIRMED_REQUIREMENT"] | Literal["INVESTIGATION"] | None | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

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
        if requirement is not UNSET:
            field_dict["requirement"] = requirement
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_investigation_citation import ReviewInvestigationCitation  # noqa: PLC0415
        from ..models.review_requirement_target import ReviewRequirementTarget  # noqa: PLC0415

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

        def _parse_requirement(data: object) -> None | ReviewRequirementTarget | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                requirement_type_0 = ReviewRequirementTarget.from_dict(data)

                return requirement_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReviewRequirementTarget | Unset, data)

        requirement = _parse_requirement(d.pop("requirement", UNSET))

        def _parse_source(
            data: object,
        ) -> Literal["CONFIRMED_REQUIREMENT"] | Literal["INVESTIGATION"] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not (type(data) is str and data == "CONFIRMED_REQUIREMENT"):
                    raise TypeError()
                componentsschemas_kian_finding_source_type_0 = cast(
                    Literal["CONFIRMED_REQUIREMENT"], data
                )
                if componentsschemas_kian_finding_source_type_0 != "CONFIRMED_REQUIREMENT":
                    raise ValueError(
                        f"/components/schemas/KianFindingSource_type_0 must match const 'CONFIRMED_REQUIREMENT', got '{componentsschemas_kian_finding_source_type_0}'"
                    )
                return componentsschemas_kian_finding_source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "INVESTIGATION"):
                    raise TypeError()
                componentsschemas_kian_finding_source_type_1 = cast(Literal["INVESTIGATION"], data)
                if componentsschemas_kian_finding_source_type_1 != "INVESTIGATION":
                    raise ValueError(
                        f"/components/schemas/KianFindingSource_type_1 must match const 'INVESTIGATION', got '{componentsschemas_kian_finding_source_type_1}'"
                    )
                return componentsschemas_kian_finding_source_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["CONFIRMED_REQUIREMENT"] | Literal["INVESTIGATION"] | None | Unset, data
            )

        source = _parse_source(d.pop("source", UNSET))

        review_investigation_finding = cls(
            area=area,
            assessment_id=assessment_id,
            citations=citations,
            detail=detail,
            title=title,
            requirement=requirement,
            source=source,
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
