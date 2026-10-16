from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="FileReviewRequest")


@_attrs_define
class FileReviewRequest:
    """Whole files selected at one exact pushed commit.

    Attributes:
        commit_sha (str): The exact pushed commit whose whole files are reviewed.
        paths (list[str]): Between one and twenty exact repository-relative file paths.
    """

    commit_sha: str
    paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        commit_sha = self.commit_sha

        paths = self.paths

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "commit_sha": commit_sha,
                "paths": paths,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        commit_sha = d.pop("commit_sha")

        paths = cast(list[str], d.pop("paths"))

        file_review_request = cls(
            commit_sha=commit_sha,
            paths=paths,
        )

        return file_review_request
