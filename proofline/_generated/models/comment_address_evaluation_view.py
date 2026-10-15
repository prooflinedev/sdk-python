from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.comment_address_outcome import CommentAddressOutcome

T = TypeVar("T", bound="CommentAddressEvaluationView")


@_attrs_define
class CommentAddressEvaluationView:
    """One stored post-merge judgment of a finding comment.

    Attributes:
        evaluated_at (datetime.datetime): When the evaluation was made.
        outcome (CommentAddressOutcome):
        reason (str): Server-authored reason. Render as text.
    """

    evaluated_at: datetime.datetime
    outcome: CommentAddressOutcome
    reason: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        evaluated_at = self.evaluated_at.isoformat()

        outcome = self.outcome.value

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "evaluated_at": evaluated_at,
                "outcome": outcome,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        evaluated_at = datetime.datetime.fromisoformat(d.pop("evaluated_at"))

        outcome = CommentAddressOutcome(d.pop("outcome"))

        reason = d.pop("reason")

        comment_address_evaluation_view = cls(
            evaluated_at=evaluated_at,
            outcome=outcome,
            reason=reason,
        )

        comment_address_evaluation_view.additional_properties = d
        return comment_address_evaluation_view

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
