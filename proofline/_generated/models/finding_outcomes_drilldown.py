from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.finding_outcomes_outcome import FindingOutcomesOutcome
from ..models.finding_outcomes_post_merge_outcome import FindingOutcomesPostMergeOutcome
from ..models.finding_outcomes_selector import FindingOutcomesSelector
from ..types import UNSET, Unset

T = TypeVar("T", bound="FindingOutcomesDrilldown")


@_attrs_define
class FindingOutcomesDrilldown:
    """
    Attributes:
        group_key (str): The `group_key` query value that limits the listed series to this count's group.
        selector (FindingOutcomesSelector):
        outcome (FindingOutcomesOutcome | None | Unset): The `outcome` query value for an `outcome` selector, and null
            for every other
             selector.
        post_merge (FindingOutcomesPostMergeOutcome | None | Unset): The `post_merge` query value for a `post_merge`
            selector, and null for every other
             selector.
    """

    group_key: str
    selector: FindingOutcomesSelector
    outcome: FindingOutcomesOutcome | None | Unset = UNSET
    post_merge: FindingOutcomesPostMergeOutcome | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_key = self.group_key

        selector = self.selector.value

        outcome: None | str | Unset
        if isinstance(self.outcome, Unset):
            outcome = UNSET
        elif isinstance(self.outcome, FindingOutcomesOutcome):
            outcome = self.outcome.value
        else:
            outcome = self.outcome

        post_merge: None | str | Unset
        if isinstance(self.post_merge, Unset):
            post_merge = UNSET
        elif isinstance(self.post_merge, FindingOutcomesPostMergeOutcome):
            post_merge = self.post_merge.value
        else:
            post_merge = self.post_merge

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "group_key": group_key,
                "selector": selector,
            }
        )
        if outcome is not UNSET:
            field_dict["outcome"] = outcome
        if post_merge is not UNSET:
            field_dict["post_merge"] = post_merge

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        group_key = d.pop("group_key")

        selector = FindingOutcomesSelector(d.pop("selector"))

        def _parse_outcome(data: object) -> FindingOutcomesOutcome | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                outcome_type_0 = FindingOutcomesOutcome(data)

                return outcome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingOutcomesOutcome | None | Unset, data)

        outcome = _parse_outcome(d.pop("outcome", UNSET))

        def _parse_post_merge(data: object) -> FindingOutcomesPostMergeOutcome | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                post_merge_type_0 = FindingOutcomesPostMergeOutcome(data)

                return post_merge_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingOutcomesPostMergeOutcome | None | Unset, data)

        post_merge = _parse_post_merge(d.pop("post_merge", UNSET))

        finding_outcomes_drilldown = cls(
            group_key=group_key,
            selector=selector,
            outcome=outcome,
            post_merge=post_merge,
        )

        finding_outcomes_drilldown.additional_properties = d
        return finding_outcomes_drilldown

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
