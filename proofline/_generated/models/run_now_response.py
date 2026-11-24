from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_warning import ModelWarning


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
           model_warning (ModelWarning | None | Unset): Why this review runs without its model and checks fixed rules only,
                for a caller that started it without reading the offer's warning.
    """

    automatic_reviews_paused: bool
    existing: bool
    review_id: UUID
    run_number: int
    model_warning: ModelWarning | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_warning import ModelWarning  # noqa: PLC0415

        automatic_reviews_paused = self.automatic_reviews_paused

        existing = self.existing

        review_id = str(self.review_id)

        run_number = self.run_number

        model_warning: dict[str, Any] | None | Unset
        if isinstance(self.model_warning, Unset):
            model_warning = UNSET
        elif isinstance(self.model_warning, ModelWarning):
            model_warning = self.model_warning.to_dict()
        else:
            model_warning = self.model_warning

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
        if model_warning is not UNSET:
            field_dict["model_warning"] = model_warning

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_warning import ModelWarning  # noqa: PLC0415

        d = dict(src_dict)
        automatic_reviews_paused = d.pop("automatic_reviews_paused")

        existing = d.pop("existing")

        review_id = UUID(d.pop("review_id"))

        run_number = d.pop("run_number")

        def _parse_model_warning(data: object) -> ModelWarning | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                model_warning_type_0 = ModelWarning.from_dict(data)

                return model_warning_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelWarning | None | Unset, data)

        model_warning = _parse_model_warning(d.pop("model_warning", UNSET))

        run_now_response = cls(
            automatic_reviews_paused=automatic_reviews_paused,
            existing=existing,
            review_id=review_id,
            run_number=run_number,
            model_warning=model_warning,
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
