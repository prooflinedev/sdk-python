from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RelatedReview")


@_attrs_define
class RelatedReview:
    """
    Attributes:
        created_at (datetime.datetime): When the related review was created.
        public_key (str): The related review's stable public address.
        relation (str): A direct lineage relation, `EARLIER_RUN` / `LATER_RUN` when the two
             reviews share a pull request without a direct lineage edge, or
             `LOCAL_REVIEW` for the pull request author's local review of exactly
             the same change.
        review_id (UUID): The related review's identifier.
        status (str): The related review's lifecycle status.
        head_commit_sha (None | str | Unset): The head commit the related review is pinned to. Absent when it recorded
            none.
        run_number (int | None | Unset): The related review's one-based ordinal within its pull request. Absent for a
            review that is not of a pull request.
    """

    created_at: datetime.datetime
    public_key: str
    relation: str
    review_id: UUID
    status: str
    head_commit_sha: None | str | Unset = UNSET
    run_number: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        public_key = self.public_key

        relation = self.relation

        review_id = str(self.review_id)

        status = self.status

        head_commit_sha: None | str | Unset
        if isinstance(self.head_commit_sha, Unset):
            head_commit_sha = UNSET
        else:
            head_commit_sha = self.head_commit_sha

        run_number: int | None | Unset
        if isinstance(self.run_number, Unset):
            run_number = UNSET
        else:
            run_number = self.run_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "public_key": public_key,
                "relation": relation,
                "review_id": review_id,
                "status": status,
            }
        )
        if head_commit_sha is not UNSET:
            field_dict["head_commit_sha"] = head_commit_sha
        if run_number is not UNSET:
            field_dict["run_number"] = run_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        public_key = d.pop("public_key")

        relation = d.pop("relation")

        review_id = UUID(d.pop("review_id"))

        status = d.pop("status")

        def _parse_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_sha = _parse_head_commit_sha(d.pop("head_commit_sha", UNSET))

        def _parse_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        run_number = _parse_run_number(d.pop("run_number", UNSET))

        related_review = cls(
            created_at=created_at,
            public_key=public_key,
            relation=relation,
            review_id=review_id,
            status=status,
            head_commit_sha=head_commit_sha,
            run_number=run_number,
        )

        related_review.additional_properties = d
        return related_review

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
