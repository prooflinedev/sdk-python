from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LinkedIssueCapture")


@_attrs_define
class LinkedIssueCapture:
    """The count and outcome of a review's linked-issue receipt. Issue numbers,
    titles and the receipt's gaps stay in the receipt.

       Attributes:
           captured_count (int): How many issues the review captured as context.
           outcome (Literal['NO_REFERENCES'] | Literal['NOT_CONFIGURED'] | Literal['PREPARED'] |
               Literal['SOURCE_UNAVAILABLE']): What the review's linked-issue preparation found.
    """

    captured_count: int
    outcome: (
        Literal["NO_REFERENCES"]
        | Literal["NOT_CONFIGURED"]
        | Literal["PREPARED"]
        | Literal["SOURCE_UNAVAILABLE"]
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        captured_count = self.captured_count

        outcome: (
            Literal["NO_REFERENCES"]
            | Literal["NOT_CONFIGURED"]
            | Literal["PREPARED"]
            | Literal["SOURCE_UNAVAILABLE"]
        )
        outcome = self.outcome

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "captured_count": captured_count,
                "outcome": outcome,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        captured_count = d.pop("captured_count")

        def _parse_outcome(
            data: object,
        ) -> (
            Literal["NO_REFERENCES"]
            | Literal["NOT_CONFIGURED"]
            | Literal["PREPARED"]
            | Literal["SOURCE_UNAVAILABLE"]
        ):
            try:
                if not (type(data) is str and data == "NOT_CONFIGURED"):
                    raise TypeError()
                componentsschemas_linked_issue_outcome_type_0 = cast(
                    Literal["NOT_CONFIGURED"], data
                )
                if componentsschemas_linked_issue_outcome_type_0 != "NOT_CONFIGURED":
                    raise ValueError(
                        f"/components/schemas/LinkedIssueOutcome_type_0 must match const 'NOT_CONFIGURED', got '{componentsschemas_linked_issue_outcome_type_0}'"
                    )
                return componentsschemas_linked_issue_outcome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NO_REFERENCES"):
                    raise TypeError()
                componentsschemas_linked_issue_outcome_type_1 = cast(Literal["NO_REFERENCES"], data)
                if componentsschemas_linked_issue_outcome_type_1 != "NO_REFERENCES":
                    raise ValueError(
                        f"/components/schemas/LinkedIssueOutcome_type_1 must match const 'NO_REFERENCES', got '{componentsschemas_linked_issue_outcome_type_1}'"
                    )
                return componentsschemas_linked_issue_outcome_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "PREPARED"):
                    raise TypeError()
                componentsschemas_linked_issue_outcome_type_2 = cast(Literal["PREPARED"], data)
                if componentsschemas_linked_issue_outcome_type_2 != "PREPARED":
                    raise ValueError(
                        f"/components/schemas/LinkedIssueOutcome_type_2 must match const 'PREPARED', got '{componentsschemas_linked_issue_outcome_type_2}'"
                    )
                return componentsschemas_linked_issue_outcome_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "SOURCE_UNAVAILABLE"):
                raise TypeError()
            componentsschemas_linked_issue_outcome_type_3 = cast(
                Literal["SOURCE_UNAVAILABLE"], data
            )
            if componentsschemas_linked_issue_outcome_type_3 != "SOURCE_UNAVAILABLE":
                raise ValueError(
                    f"/components/schemas/LinkedIssueOutcome_type_3 must match const 'SOURCE_UNAVAILABLE', got '{componentsschemas_linked_issue_outcome_type_3}'"
                )
            return componentsschemas_linked_issue_outcome_type_3

        outcome = _parse_outcome(d.pop("outcome"))

        linked_issue_capture = cls(
            captured_count=captured_count,
            outcome=outcome,
        )

        linked_issue_capture.additional_properties = d
        return linked_issue_capture

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
