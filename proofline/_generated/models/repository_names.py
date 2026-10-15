from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.repository_name import RepositoryName


T = TypeVar("T", bound="RepositoryNames")


@_attrs_define
class RepositoryNames:
    """
    Attributes:
        repositories (list[RepositoryName]): The organization's repositories that are not deleted, ordered by name; a
             repository-restricted token sees only its allowlist.
    """

    repositories: list[RepositoryName]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repositories = []
        for repositories_item_data in self.repositories:
            repositories_item = repositories_item_data.to_dict()
            repositories.append(repositories_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repositories": repositories,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repository_name import RepositoryName  # noqa: PLC0415

        d = dict(src_dict)
        repositories = []
        _repositories = d.pop("repositories")
        for repositories_item_data in _repositories:
            repositories_item = RepositoryName.from_dict(repositories_item_data)

            repositories.append(repositories_item)

        repository_names = cls(
            repositories=repositories,
        )

        repository_names.additional_properties = d
        return repository_names

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
