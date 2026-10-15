from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.not_assessed_view import NotAssessedView


T = TypeVar("T", bound="OpenItemsView")


@_attrs_define
class OpenItemsView:
    """Recorded unresolved findings, accepted risks and assessment gaps.
    Coverage and notification suppression do not resolve a finding. These
    scalar counts make no claim about current heads, evaluated scope or threads.

       Attributes:
           accepted_risks (int): Finding series whose current decision is an unexpired `ACCEPTED_RISK`.
           not_assessed (list[NotAssessedView]): Recorded assessment gaps, including explicit policy exclusions.
           open_findings (int): Unresolved recorded finding series, including notification-suppressed
                findings, decisions whose dismissal or risk acceptance expired, and
                earlier published series of the pull request that this review did not
                find again.
           serious_findings (int): The `SERIOUS` findings among `open_findings`.
    """

    accepted_risks: int
    not_assessed: list[NotAssessedView]
    open_findings: int
    serious_findings: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accepted_risks = self.accepted_risks

        not_assessed = []
        for not_assessed_item_data in self.not_assessed:
            not_assessed_item = not_assessed_item_data.to_dict()
            not_assessed.append(not_assessed_item)

        open_findings = self.open_findings

        serious_findings = self.serious_findings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accepted_risks": accepted_risks,
                "not_assessed": not_assessed,
                "open_findings": open_findings,
                "serious_findings": serious_findings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.not_assessed_view import NotAssessedView  # noqa: PLC0415

        d = dict(src_dict)
        accepted_risks = d.pop("accepted_risks")

        not_assessed = []
        _not_assessed = d.pop("not_assessed")
        for not_assessed_item_data in _not_assessed:
            not_assessed_item = NotAssessedView.from_dict(not_assessed_item_data)

            not_assessed.append(not_assessed_item)

        open_findings = d.pop("open_findings")

        serious_findings = d.pop("serious_findings")

        open_items_view = cls(
            accepted_risks=accepted_risks,
            not_assessed=not_assessed,
            open_findings=open_findings,
            serious_findings=serious_findings,
        )

        open_items_view.additional_properties = d
        return open_items_view

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
