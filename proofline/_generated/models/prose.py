from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Prose")


@_attrs_define
class Prose:
    """
    Attributes:
        headline (str): At most 120 characters.
        notable_paths (list[str]): Paths in the pinned diff the prose calls out.
        paragraphs (list[str]): At most three of at most 400 characters; one on the `SHORT` route.
    """

    headline: str
    notable_paths: list[str]
    paragraphs: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        headline = self.headline

        notable_paths = self.notable_paths

        paragraphs = self.paragraphs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "headline": headline,
                "notable_paths": notable_paths,
                "paragraphs": paragraphs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        headline = d.pop("headline")

        notable_paths = cast(list[str], d.pop("notable_paths"))

        paragraphs = cast(list[str], d.pop("paragraphs"))

        prose = cls(
            headline=headline,
            notable_paths=notable_paths,
            paragraphs=paragraphs,
        )

        prose.additional_properties = d
        return prose

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
