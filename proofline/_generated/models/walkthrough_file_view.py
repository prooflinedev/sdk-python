from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WalkthroughFileView")


@_attrs_define
class WalkthroughFileView:
    """
    Attributes:
        additions (int):
        change (str): GitHub's change status, upper case, such as `ADDED` or `RENAMED`.
        deletions (int):
        generated (bool): Whether `line` is model-authored.
        line (str): A model sentence, or the deterministic line when there is none.
        path (str):
        depth (None | str | Unset): The route plan's depth tier. Absent for a file the review did not
             evaluate.
        previous_path (None | str | Unset):
        skip_class (None | str | Unset): Why the review did not evaluate the file, such as `LOCKFILE` or
             `REPOSITORY_FILTER`.
    """

    additions: int
    change: str
    deletions: int
    generated: bool
    line: str
    path: str
    depth: None | str | Unset = UNSET
    previous_path: None | str | Unset = UNSET
    skip_class: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        additions = self.additions

        change = self.change

        deletions = self.deletions

        generated = self.generated

        line = self.line

        path = self.path

        depth: None | str | Unset
        if isinstance(self.depth, Unset):
            depth = UNSET
        else:
            depth = self.depth

        previous_path: None | str | Unset
        if isinstance(self.previous_path, Unset):
            previous_path = UNSET
        else:
            previous_path = self.previous_path

        skip_class: None | str | Unset
        if isinstance(self.skip_class, Unset):
            skip_class = UNSET
        else:
            skip_class = self.skip_class

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "additions": additions,
                "change": change,
                "deletions": deletions,
                "generated": generated,
                "line": line,
                "path": path,
            }
        )
        if depth is not UNSET:
            field_dict["depth"] = depth
        if previous_path is not UNSET:
            field_dict["previous_path"] = previous_path
        if skip_class is not UNSET:
            field_dict["skip_class"] = skip_class

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        additions = d.pop("additions")

        change = d.pop("change")

        deletions = d.pop("deletions")

        generated = d.pop("generated")

        line = d.pop("line")

        path = d.pop("path")

        def _parse_depth(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        depth = _parse_depth(d.pop("depth", UNSET))

        def _parse_previous_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        previous_path = _parse_previous_path(d.pop("previous_path", UNSET))

        def _parse_skip_class(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        skip_class = _parse_skip_class(d.pop("skip_class", UNSET))

        walkthrough_file_view = cls(
            additions=additions,
            change=change,
            deletions=deletions,
            generated=generated,
            line=line,
            path=path,
            depth=depth,
            previous_path=previous_path,
            skip_class=skip_class,
        )

        walkthrough_file_view.additional_properties = d
        return walkthrough_file_view

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
