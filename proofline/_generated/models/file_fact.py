from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.review_depth import ReviewDepth
from ..types import UNSET, Unset

T = TypeVar("T", bound="FileFact")


@_attrs_define
class FileFact:
    """
    Attributes:
        additions (int): Lines added in this file's recorded diff.
        deletions (int): Lines deleted in this file's recorded diff.
        depth (ReviewDepth): The depth the applied route plan read a file at.
        path (str): The repository-relative path of the changed file.
        status (str): GitHub's file status: `added`, `modified`, `removed`, `renamed` and so on.
        previous_path (None | str | Unset): The path before a rename.
    """

    additions: int
    deletions: int
    depth: ReviewDepth
    path: str
    status: str
    previous_path: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        additions = self.additions

        deletions = self.deletions

        depth = self.depth.value

        path = self.path

        status = self.status

        previous_path: None | str | Unset
        if isinstance(self.previous_path, Unset):
            previous_path = UNSET
        else:
            previous_path = self.previous_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "additions": additions,
                "deletions": deletions,
                "depth": depth,
                "path": path,
                "status": status,
            }
        )
        if previous_path is not UNSET:
            field_dict["previous_path"] = previous_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        additions = d.pop("additions")

        deletions = d.pop("deletions")

        depth = ReviewDepth(d.pop("depth"))

        path = d.pop("path")

        status = d.pop("status")

        def _parse_previous_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        previous_path = _parse_previous_path(d.pop("previous_path", UNSET))

        file_fact = cls(
            additions=additions,
            deletions=deletions,
            depth=depth,
            path=path,
            status=status,
            previous_path=previous_path,
        )

        file_fact.additional_properties = d
        return file_fact

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
