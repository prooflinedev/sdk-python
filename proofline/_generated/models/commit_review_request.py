from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CommitReviewRequest")


@_attrs_define
class CommitReviewRequest:
    """Pushed commits to review: the exact base the change is compared with and
    the exact head it ends at.

       Attributes:
           base_commit_sha (str): The full 40-character commit the change is compared with. GitHub must
                have it in this repository, and it must be an ancestor of the head.
           head_commit_sha (str): The full 40-character commit the change ends at. GitHub must have it
                in this repository.
    """

    base_commit_sha: str
    head_commit_sha: str

    def to_dict(self) -> dict[str, Any]:
        base_commit_sha = self.base_commit_sha

        head_commit_sha = self.head_commit_sha

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base_commit_sha": base_commit_sha,
                "head_commit_sha": head_commit_sha,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_commit_sha = d.pop("base_commit_sha")

        head_commit_sha = d.pop("head_commit_sha")

        commit_review_request = cls(
            base_commit_sha=base_commit_sha,
            head_commit_sha=head_commit_sha,
        )

        return commit_review_request
