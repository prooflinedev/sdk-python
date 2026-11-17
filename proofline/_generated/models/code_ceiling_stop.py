from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CodeCeilingStop")


@_attrs_define
class CodeCeilingStop:
    """What a code assessment had read when its head's spending ceiling stopped
    it. A rerun of the same commit runs under the same ceiling.

       Attributes:
           changed_files (int): The distinct files the reviewed change touched.
           unfinished_paths (list[str]): The changed files of each part of the change the ceiling stopped or
                never reached, in review order. The assessment may have read some of
                their changed lines, so this lists files it did not finish. Empty
                when the ceiling stopped it after every part was read.
    """

    changed_files: int
    unfinished_paths: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        changed_files = self.changed_files

        unfinished_paths = self.unfinished_paths

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "changed_files": changed_files,
                "unfinished_paths": unfinished_paths,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        changed_files = d.pop("changed_files")

        unfinished_paths = cast(list[str], d.pop("unfinished_paths"))

        code_ceiling_stop = cls(
            changed_files=changed_files,
            unfinished_paths=unfinished_paths,
        )

        code_ceiling_stop.additional_properties = d
        return code_ceiling_stop

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
