from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.review_filters import ReviewFilters
    from ..models.review_summary import ReviewSummary


T = TypeVar("T", bound="ReviewPage")


@_attrs_define
class ReviewPage:
    """
    Attributes:
        filters (ReviewFilters):
        items (list[ReviewSummary]): The reviews on this page, newest first.
        truncated (bool): Whether more reviews match the query beyond this page.
        applied_query (None | str | Unset): The exact structured query applied before pagination.
        next_cursor (None | str | Unset): The cursor that requests the next page. Null when `truncated` is false.
    """

    filters: ReviewFilters
    items: list[ReviewSummary]
    truncated: bool
    applied_query: None | str | Unset = UNSET
    next_cursor: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filters = self.filters.to_dict()

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        truncated = self.truncated

        applied_query: None | str | Unset
        if isinstance(self.applied_query, Unset):
            applied_query = UNSET
        else:
            applied_query = self.applied_query

        next_cursor: None | str | Unset
        if isinstance(self.next_cursor, Unset):
            next_cursor = UNSET
        else:
            next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filters": filters,
                "items": items,
                "truncated": truncated,
            }
        )
        if applied_query is not UNSET:
            field_dict["applied_query"] = applied_query
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_filters import ReviewFilters  # noqa: PLC0415
        from ..models.review_summary import ReviewSummary  # noqa: PLC0415

        d = dict(src_dict)
        filters = ReviewFilters.from_dict(d.pop("filters"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = ReviewSummary.from_dict(items_item_data)

            items.append(items_item)

        truncated = d.pop("truncated")

        def _parse_applied_query(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        applied_query = _parse_applied_query(d.pop("applied_query", UNSET))

        def _parse_next_cursor(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor", UNSET))

        review_page = cls(
            filters=filters,
            items=items,
            truncated=truncated,
            applied_query=applied_query,
            next_cursor=next_cursor,
        )

        review_page.additional_properties = d
        return review_page

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
