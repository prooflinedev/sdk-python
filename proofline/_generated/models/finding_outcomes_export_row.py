from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.finding_outcomes_group_by import FindingOutcomesGroupBy

if TYPE_CHECKING:
    from ..models.finding_outcomes_count import FindingOutcomesCount
    from ..models.finding_outcomes_outcome_count import FindingOutcomesOutcomeCount
    from ..models.finding_outcomes_post_merge_counts import FindingOutcomesPostMergeCounts


T = TypeVar("T", bound="FindingOutcomesExportRow")


@_attrs_define
class FindingOutcomesExportRow:
    """Exact shared aggregate counts for one admitted group and requested window.

    Attributes:
        code_changed (FindingOutcomesCount):
        dataset_version (int): The row contract version, always `1`.
        external_validation_denominator (int): Human-validated series; excludes automatic coverage and unrecorded
            outcomes.
        from_ (datetime.datetime): The inclusive start of the requested first-publication window.
        group_by (FindingOutcomesGroupBy):
        key (str): The grouping value: a repository or environment ID, a risk domain, a severity or a
             review kind, as `group_by` selects.
        limitations (list[str]): Gaps in publication history that keep findings outside these counts; they mean
             missing history, not zero findings.
        name (str): The group's display name: the repository's full name (or `Repository` and its ID when
             no name is recorded), the environment's display name, or otherwise `key`.
        organization_id (UUID): The organization whose findings are counted.
        outcomes (list[FindingOutcomesOutcomeCount]): One count per outcome, always all six `FindingOutcomesOutcome`
            values in a fixed order.
        post_merge (FindingOutcomesPostMergeCounts):
        published (int): Finding series in the group whose first publication falls inside the window.
        to (datetime.datetime): The exclusive end of the requested first-publication window.
    """

    code_changed: FindingOutcomesCount
    dataset_version: int
    external_validation_denominator: int
    from_: datetime.datetime
    group_by: FindingOutcomesGroupBy
    key: str
    limitations: list[str]
    name: str
    organization_id: UUID
    outcomes: list[FindingOutcomesOutcomeCount]
    post_merge: FindingOutcomesPostMergeCounts
    published: int
    to: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code_changed = self.code_changed.to_dict()

        dataset_version = self.dataset_version

        external_validation_denominator = self.external_validation_denominator

        from_ = self.from_.isoformat()

        group_by = self.group_by.value

        key = self.key

        limitations = self.limitations

        name = self.name

        organization_id = str(self.organization_id)

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        post_merge = self.post_merge.to_dict()

        published = self.published

        to = self.to.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code_changed": code_changed,
                "dataset_version": dataset_version,
                "external_validation_denominator": external_validation_denominator,
                "from": from_,
                "group_by": group_by,
                "key": key,
                "limitations": limitations,
                "name": name,
                "organization_id": organization_id,
                "outcomes": outcomes,
                "post_merge": post_merge,
                "published": published,
                "to": to,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_outcomes_count import FindingOutcomesCount  # noqa: PLC0415
        from ..models.finding_outcomes_outcome_count import (
            FindingOutcomesOutcomeCount,  # noqa: PLC0415
        )
        from ..models.finding_outcomes_post_merge_counts import (
            FindingOutcomesPostMergeCounts,  # noqa: PLC0415
        )

        d = dict(src_dict)
        code_changed = FindingOutcomesCount.from_dict(d.pop("code_changed"))

        dataset_version = d.pop("dataset_version")

        external_validation_denominator = d.pop("external_validation_denominator")

        from_ = datetime.datetime.fromisoformat(d.pop("from"))

        group_by = FindingOutcomesGroupBy(d.pop("group_by"))

        key = d.pop("key")

        limitations = cast(list[str], d.pop("limitations"))

        name = d.pop("name")

        organization_id = UUID(d.pop("organization_id"))

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = FindingOutcomesOutcomeCount.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        post_merge = FindingOutcomesPostMergeCounts.from_dict(d.pop("post_merge"))

        published = d.pop("published")

        to = datetime.datetime.fromisoformat(d.pop("to"))

        finding_outcomes_export_row = cls(
            code_changed=code_changed,
            dataset_version=dataset_version,
            external_validation_denominator=external_validation_denominator,
            from_=from_,
            group_by=group_by,
            key=key,
            limitations=limitations,
            name=name,
            organization_id=organization_id,
            outcomes=outcomes,
            post_merge=post_merge,
            published=published,
            to=to,
        )

        finding_outcomes_export_row.additional_properties = d
        return finding_outcomes_export_row

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
