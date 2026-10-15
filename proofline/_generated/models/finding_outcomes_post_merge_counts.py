from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.finding_outcomes_post_merge_count import FindingOutcomesPostMergeCount


T = TypeVar("T", bound="FindingOutcomesPostMergeCounts")


@_attrs_define
class FindingOutcomesPostMergeCounts:
    """
    Attributes:
        judged (int): Series with a retained evaluation, rather than all published series.
        outcomes (list[FindingOutcomesPostMergeCount]): One count per post-merge outcome, always `ADDRESSED`,
            `NOT_ADDRESSED` and `INCOMPLETE`
             in that order.
    """

    judged: int
    outcomes: list[FindingOutcomesPostMergeCount]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        judged = self.judged

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "judged": judged,
                "outcomes": outcomes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_outcomes_post_merge_count import (
            FindingOutcomesPostMergeCount,  # noqa: PLC0415
        )

        d = dict(src_dict)
        judged = d.pop("judged")

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = FindingOutcomesPostMergeCount.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        finding_outcomes_post_merge_counts = cls(
            judged=judged,
            outcomes=outcomes,
        )

        finding_outcomes_post_merge_counts.additional_properties = d
        return finding_outcomes_post_merge_counts

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
