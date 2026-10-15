from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.finding_outcomes_outcome import FindingOutcomesOutcome

if TYPE_CHECKING:
    from ..models.finding_outcomes_drilldown import FindingOutcomesDrilldown
    from ..models.finding_outcomes_validation_sources import FindingOutcomesValidationSources


T = TypeVar("T", bound="FindingOutcomesOutcomeCount")


@_attrs_define
class FindingOutcomesOutcomeCount:
    """
    Attributes:
        count (int): Published finding series in the group whose latest qualifying outcome is `outcome`.
        drilldown (FindingOutcomesDrilldown):
        outcome (FindingOutcomesOutcome):
        validation_sources (FindingOutcomesValidationSources):
    """

    count: int
    drilldown: FindingOutcomesDrilldown
    outcome: FindingOutcomesOutcome
    validation_sources: FindingOutcomesValidationSources
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        drilldown = self.drilldown.to_dict()

        outcome = self.outcome.value

        validation_sources = self.validation_sources.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "drilldown": drilldown,
                "outcome": outcome,
                "validation_sources": validation_sources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_outcomes_drilldown import FindingOutcomesDrilldown  # noqa: PLC0415
        from ..models.finding_outcomes_validation_sources import (
            FindingOutcomesValidationSources,  # noqa: PLC0415
        )

        d = dict(src_dict)
        count = d.pop("count")

        drilldown = FindingOutcomesDrilldown.from_dict(d.pop("drilldown"))

        outcome = FindingOutcomesOutcome(d.pop("outcome"))

        validation_sources = FindingOutcomesValidationSources.from_dict(d.pop("validation_sources"))

        finding_outcomes_outcome_count = cls(
            count=count,
            drilldown=drilldown,
            outcome=outcome,
            validation_sources=validation_sources,
        )

        finding_outcomes_outcome_count.additional_properties = d
        return finding_outcomes_outcome_count

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
