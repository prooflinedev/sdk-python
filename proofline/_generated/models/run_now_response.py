from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RunNowResponse")


@_attrs_define
class RunNowResponse:
    """What a run-now request produced: a review of the live head, created by
    this request or found already owning the head.

       Attributes:
           automatic_reviews_paused (bool): True when automatic reviews are stopped on this pull request. The
                review ran anyway; the flag is why the page can say so.
           existing (bool): True when this head already carried a review and that one is
                returned. Clicking twice does not run twice.
           review_id (UUID): The review that owns the live head, new or existing.
           run_number (int): The review's one-based ordinal within its pull request, which
                completes the run's console address.
    """

    automatic_reviews_paused: bool
    existing: bool
    review_id: UUID
    run_number: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        automatic_reviews_paused = self.automatic_reviews_paused

        existing = self.existing

        review_id = str(self.review_id)

        run_number = self.run_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "automatic_reviews_paused": automatic_reviews_paused,
                "existing": existing,
                "review_id": review_id,
                "run_number": run_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        automatic_reviews_paused = d.pop("automatic_reviews_paused")

        existing = d.pop("existing")

        review_id = UUID(d.pop("review_id"))

        run_number = d.pop("run_number")

        run_now_response = cls(
            automatic_reviews_paused=automatic_reviews_paused,
            existing=existing,
            review_id=review_id,
            run_number=run_number,
        )

        run_now_response.additional_properties = d
        return run_now_response

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
