from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="FileScope")


@_attrs_define
class FileScope:
    """The retained selection, not a digest of file contents. Its identity uses
    a version prefix and length-framed UTF-8 paths in their sorted order.

       Attributes:
           paths (list[str]):
           paths_digest (str):
    """

    paths: list[str]
    paths_digest: str

    def to_dict(self) -> dict[str, Any]:
        paths = self.paths

        paths_digest = self.paths_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "paths": paths,
                "paths_digest": paths_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        paths = cast(list[str], d.pop("paths"))

        paths_digest = d.pop("paths_digest")

        file_scope = cls(
            paths=paths,
            paths_digest=paths_digest,
        )

        return file_scope
