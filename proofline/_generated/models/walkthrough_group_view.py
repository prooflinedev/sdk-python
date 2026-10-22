from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.walkthrough_file_view import WalkthroughFileView


T = TypeVar("T", bound="WalkthroughGroupView")


@_attrs_define
class WalkthroughGroupView:
    """
    Attributes:
        files (list[WalkthroughFileView]):
        kind (str): `FEATURE`, `FIX`, `REFACTOR`, `CONFIGURATION`, `INFRASTRUCTURE`,
             `DATA`, `DEPENDENCIES`, `TESTS` or `DOCS`.
        title (str):
        description (None | str | Unset):
    """

    files: list[WalkthroughFileView]
    kind: str
    title: str
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        kind = self.kind

        title = self.title

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "kind": kind,
                "title": title,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.walkthrough_file_view import WalkthroughFileView  # noqa: PLC0415

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = WalkthroughFileView.from_dict(files_item_data)

            files.append(files_item)

        kind = d.pop("kind")

        title = d.pop("title")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        walkthrough_group_view = cls(
            files=files,
            kind=kind,
            title=title,
            description=description,
        )

        walkthrough_group_view.additional_properties = d
        return walkthrough_group_view

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
