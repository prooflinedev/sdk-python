from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.open_items_head_state import OpenItemsHeadState
from ..models.open_items_review_status import OpenItemsReviewStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_finding_counts import OpenFindingCounts
    from ..models.open_item_environment import OpenItemEnvironment
    from ..models.open_items_threads_type_0 import OpenItemsThreadsType0
    from ..models.open_items_threads_type_1 import OpenItemsThreadsType1


T = TypeVar("T", bound="ReviewOpenItems")


@_attrs_define
class ReviewOpenItems:
    """
    Attributes:
        accepted_risk_count (int): Finding series whose current decision is an unexpired `ACCEPTED_RISK`.
        environments (list[OpenItemEnvironment]): This review's environment assessments that are not `COMPLETED`,
            ordered
             by environment key.
        evaluated_scope_known (bool): Whether the review recorded at least one environment assessment. False
             means the evaluated scope is unknown, so an empty `environments` proves
             nothing.
        head_state (OpenItemsHeadState):
        is_latest_review (bool): Whether this review is the newest review of its pull request the caller
             can see.
        latest_review_head_state (OpenItemsHeadState):
        observed_at (datetime.datetime): When the database facts in this observation were read, all from one
             statement.
        open_findings (OpenFindingCounts):
        review_status (OpenItemsReviewStatus):
        threads (OpenItemsThreadsType0 | OpenItemsThreadsType1):
        current_head_provider_updated_at (datetime.datetime | None | Unset): GitHub's update time for the recorded pull
            request state that
             `current_head_sha` comes from. Null when none is recorded.
        current_head_sha (None | str | Unset): The pull request's head commit as Proofline last recorded it from
             GitHub. Null when no pull request state is recorded.
        latest_review_head_sha (None | str | Unset): The head commit of the newest review of this pull request the
            caller
             can see. Null when that review recorded none.
        reviewed_head_sha (None | str | Unset): The head commit this review evaluated. Null when the review recorded
             none.
    """

    accepted_risk_count: int
    environments: list[OpenItemEnvironment]
    evaluated_scope_known: bool
    head_state: OpenItemsHeadState
    is_latest_review: bool
    latest_review_head_state: OpenItemsHeadState
    observed_at: datetime.datetime
    open_findings: OpenFindingCounts
    review_status: OpenItemsReviewStatus
    threads: OpenItemsThreadsType0 | OpenItemsThreadsType1
    current_head_provider_updated_at: datetime.datetime | None | Unset = UNSET
    current_head_sha: None | str | Unset = UNSET
    latest_review_head_sha: None | str | Unset = UNSET
    reviewed_head_sha: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.open_items_threads_type_0 import OpenItemsThreadsType0  # noqa: PLC0415

        accepted_risk_count = self.accepted_risk_count

        environments = []
        for environments_item_data in self.environments:
            environments_item = environments_item_data.to_dict()
            environments.append(environments_item)

        evaluated_scope_known = self.evaluated_scope_known

        head_state = self.head_state.value

        is_latest_review = self.is_latest_review

        latest_review_head_state = self.latest_review_head_state.value

        observed_at = self.observed_at.isoformat()

        open_findings = self.open_findings.to_dict()

        review_status = self.review_status.value

        threads: dict[str, Any]
        if isinstance(self.threads, OpenItemsThreadsType0):
            threads = self.threads.to_dict()
        else:
            threads = self.threads.to_dict()

        current_head_provider_updated_at: None | str | Unset
        if isinstance(self.current_head_provider_updated_at, Unset):
            current_head_provider_updated_at = UNSET
        elif isinstance(self.current_head_provider_updated_at, datetime.datetime):
            current_head_provider_updated_at = self.current_head_provider_updated_at.isoformat()
        else:
            current_head_provider_updated_at = self.current_head_provider_updated_at

        current_head_sha: None | str | Unset
        if isinstance(self.current_head_sha, Unset):
            current_head_sha = UNSET
        else:
            current_head_sha = self.current_head_sha

        latest_review_head_sha: None | str | Unset
        if isinstance(self.latest_review_head_sha, Unset):
            latest_review_head_sha = UNSET
        else:
            latest_review_head_sha = self.latest_review_head_sha

        reviewed_head_sha: None | str | Unset
        if isinstance(self.reviewed_head_sha, Unset):
            reviewed_head_sha = UNSET
        else:
            reviewed_head_sha = self.reviewed_head_sha

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accepted_risk_count": accepted_risk_count,
                "environments": environments,
                "evaluated_scope_known": evaluated_scope_known,
                "head_state": head_state,
                "is_latest_review": is_latest_review,
                "latest_review_head_state": latest_review_head_state,
                "observed_at": observed_at,
                "open_findings": open_findings,
                "review_status": review_status,
                "threads": threads,
            }
        )
        if current_head_provider_updated_at is not UNSET:
            field_dict["current_head_provider_updated_at"] = current_head_provider_updated_at
        if current_head_sha is not UNSET:
            field_dict["current_head_sha"] = current_head_sha
        if latest_review_head_sha is not UNSET:
            field_dict["latest_review_head_sha"] = latest_review_head_sha
        if reviewed_head_sha is not UNSET:
            field_dict["reviewed_head_sha"] = reviewed_head_sha

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_finding_counts import OpenFindingCounts  # noqa: PLC0415
        from ..models.open_item_environment import OpenItemEnvironment  # noqa: PLC0415
        from ..models.open_items_threads_type_0 import OpenItemsThreadsType0  # noqa: PLC0415
        from ..models.open_items_threads_type_1 import OpenItemsThreadsType1  # noqa: PLC0415

        d = dict(src_dict)
        accepted_risk_count = d.pop("accepted_risk_count")

        environments = []
        _environments = d.pop("environments")
        for environments_item_data in _environments:
            environments_item = OpenItemEnvironment.from_dict(environments_item_data)

            environments.append(environments_item)

        evaluated_scope_known = d.pop("evaluated_scope_known")

        head_state = OpenItemsHeadState(d.pop("head_state"))

        is_latest_review = d.pop("is_latest_review")

        latest_review_head_state = OpenItemsHeadState(d.pop("latest_review_head_state"))

        observed_at = datetime.datetime.fromisoformat(d.pop("observed_at"))

        open_findings = OpenFindingCounts.from_dict(d.pop("open_findings"))

        review_status = OpenItemsReviewStatus(d.pop("review_status"))

        def _parse_threads(data: object) -> OpenItemsThreadsType0 | OpenItemsThreadsType1:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_open_items_threads_type_0 = OpenItemsThreadsType0.from_dict(data)

                return componentsschemas_open_items_threads_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_open_items_threads_type_1 = OpenItemsThreadsType1.from_dict(data)

            return componentsschemas_open_items_threads_type_1

        threads = _parse_threads(d.pop("threads"))

        def _parse_current_head_provider_updated_at(
            data: object,
        ) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                current_head_provider_updated_at_type_0 = datetime.datetime.fromisoformat(data)

                return current_head_provider_updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        current_head_provider_updated_at = _parse_current_head_provider_updated_at(
            d.pop("current_head_provider_updated_at", UNSET)
        )

        def _parse_current_head_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        current_head_sha = _parse_current_head_sha(d.pop("current_head_sha", UNSET))

        def _parse_latest_review_head_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        latest_review_head_sha = _parse_latest_review_head_sha(
            d.pop("latest_review_head_sha", UNSET)
        )

        def _parse_reviewed_head_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reviewed_head_sha = _parse_reviewed_head_sha(d.pop("reviewed_head_sha", UNSET))

        review_open_items = cls(
            accepted_risk_count=accepted_risk_count,
            environments=environments,
            evaluated_scope_known=evaluated_scope_known,
            head_state=head_state,
            is_latest_review=is_latest_review,
            latest_review_head_state=latest_review_head_state,
            observed_at=observed_at,
            open_findings=open_findings,
            review_status=review_status,
            threads=threads,
            current_head_provider_updated_at=current_head_provider_updated_at,
            current_head_sha=current_head_sha,
            latest_review_head_sha=latest_review_head_sha,
            reviewed_head_sha=reviewed_head_sha,
        )

        review_open_items.additional_properties = d
        return review_open_items

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
