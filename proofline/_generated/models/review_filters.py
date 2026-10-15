from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.author_choice import AuthorChoice
    from ..models.filter_choice import FilterChoice


T = TypeVar("T", bound="ReviewFilters")


@_attrs_define
class ReviewFilters:
    """
    Attributes:
        authors (list[AuthorChoice]): Authors of visible pull request reviews, one per GitHub user.
        environments (list[FilterChoice]): Environments assessed by at least one visible review, ordered by
             display name.
        repositories (list[FilterChoice]): Repositories that have at least one visible review, ordered by full
             name.
    """

    authors: list[AuthorChoice]
    environments: list[FilterChoice]
    repositories: list[FilterChoice]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authors = []
        for authors_item_data in self.authors:
            authors_item = authors_item_data.to_dict()
            authors.append(authors_item)

        environments = []
        for environments_item_data in self.environments:
            environments_item = environments_item_data.to_dict()
            environments.append(environments_item)

        repositories = []
        for repositories_item_data in self.repositories:
            repositories_item = repositories_item_data.to_dict()
            repositories.append(repositories_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authors": authors,
                "environments": environments,
                "repositories": repositories,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.author_choice import AuthorChoice  # noqa: PLC0415
        from ..models.filter_choice import FilterChoice  # noqa: PLC0415

        d = dict(src_dict)
        authors = []
        _authors = d.pop("authors")
        for authors_item_data in _authors:
            authors_item = AuthorChoice.from_dict(authors_item_data)

            authors.append(authors_item)

        environments = []
        _environments = d.pop("environments")
        for environments_item_data in _environments:
            environments_item = FilterChoice.from_dict(environments_item_data)

            environments.append(environments_item)

        repositories = []
        _repositories = d.pop("repositories")
        for repositories_item_data in _repositories:
            repositories_item = FilterChoice.from_dict(repositories_item_data)

            repositories.append(repositories_item)

        review_filters = cls(
            authors=authors,
            environments=environments,
            repositories=repositories,
        )

        review_filters.additional_properties = d
        return review_filters

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
