from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.finding_outcomes_drilldown import FindingOutcomesDrilldown


T = TypeVar("T", bound="FindingOutcomesCount")


@_attrs_define
class FindingOutcomesCount:
    """
    Attributes:
        count (int): Published finding series in the group whose series disposition is `RESOLVED_BY_PUSH`.
        drilldown (FindingOutcomesDrilldown):
    """

    count: int
    drilldown: FindingOutcomesDrilldown
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        drilldown = self.drilldown.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
                "drilldown": drilldown,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_outcomes_drilldown import FindingOutcomesDrilldown  # noqa: PLC0415

        d = dict(src_dict)
        count = d.pop("count")

        drilldown = FindingOutcomesDrilldown.from_dict(d.pop("drilldown"))

        finding_outcomes_count = cls(
            count=count,
            drilldown=drilldown,
        )

        finding_outcomes_count.additional_properties = d
        return finding_outcomes_count

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
