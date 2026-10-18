from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.change_diagram_kind_view import ChangeDiagramKindView
from ..models.change_diagram_outcome_type_0 import ChangeDiagramOutcomeType0
from ..types import UNSET, Unset

T = TypeVar("T", bound="ChangeDiagramView")


@_attrs_define
class ChangeDiagramView:
    """The change-level diagram recorded for a review, or why there is none.

    Attributes:
        legend (list[str]): Markdown lines under the diagram: which environment and snapshot its
             dashed relations come from, or which environment was not read.
        outcome (ChangeDiagramOutcomeType0 | Literal['DECISION_UNAVAILABLE'] | Literal['INDEX_INCOMPLETE'] |
            Literal['NO_INTERACTION'] | Literal['OVER_CAPS']):
        kind (ChangeDiagramKindView | None | Unset): Diagram format when a diagram was drawn; otherwise null.
        mermaid (None | str | Unset): Mermaid source the server generated from the stored graph. Every
             label is escaped, and no model wrote any of it. Absent unless
             `outcome` is `DRAWN`.
    """

    legend: list[str]
    outcome: (
        ChangeDiagramOutcomeType0
        | Literal["DECISION_UNAVAILABLE"]
        | Literal["INDEX_INCOMPLETE"]
        | Literal["NO_INTERACTION"]
        | Literal["OVER_CAPS"]
    )
    kind: ChangeDiagramKindView | None | Unset = UNSET
    mermaid: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        legend = self.legend

        outcome: (
            Literal["DECISION_UNAVAILABLE"]
            | Literal["INDEX_INCOMPLETE"]
            | Literal["NO_INTERACTION"]
            | Literal["OVER_CAPS"]
            | str
        )
        if isinstance(self.outcome, ChangeDiagramOutcomeType0):
            outcome = self.outcome.value
        else:
            outcome = self.outcome

        kind: None | str | Unset
        if isinstance(self.kind, Unset):
            kind = UNSET
        elif isinstance(self.kind, ChangeDiagramKindView):
            kind = self.kind.value
        else:
            kind = self.kind

        mermaid: None | str | Unset
        if isinstance(self.mermaid, Unset):
            mermaid = UNSET
        else:
            mermaid = self.mermaid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "legend": legend,
                "outcome": outcome,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind
        if mermaid is not UNSET:
            field_dict["mermaid"] = mermaid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        legend = cast(list[str], d.pop("legend"))

        def _parse_outcome(
            data: object,
        ) -> (
            ChangeDiagramOutcomeType0
            | Literal["DECISION_UNAVAILABLE"]
            | Literal["INDEX_INCOMPLETE"]
            | Literal["NO_INTERACTION"]
            | Literal["OVER_CAPS"]
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_change_diagram_outcome_type_0 = ChangeDiagramOutcomeType0(data)

                return componentsschemas_change_diagram_outcome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NO_INTERACTION"):
                    raise TypeError()
                componentsschemas_change_diagram_outcome_type_1 = cast(
                    Literal["NO_INTERACTION"], data
                )
                if componentsschemas_change_diagram_outcome_type_1 != "NO_INTERACTION":
                    raise ValueError(
                        f"/components/schemas/ChangeDiagramOutcome_type_1 must match const 'NO_INTERACTION', got '{componentsschemas_change_diagram_outcome_type_1}'"
                    )
                return componentsschemas_change_diagram_outcome_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "INDEX_INCOMPLETE"):
                    raise TypeError()
                componentsschemas_change_diagram_outcome_type_2 = cast(
                    Literal["INDEX_INCOMPLETE"], data
                )
                if componentsschemas_change_diagram_outcome_type_2 != "INDEX_INCOMPLETE":
                    raise ValueError(
                        f"/components/schemas/ChangeDiagramOutcome_type_2 must match const 'INDEX_INCOMPLETE', got '{componentsschemas_change_diagram_outcome_type_2}'"
                    )
                return componentsschemas_change_diagram_outcome_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "OVER_CAPS"):
                    raise TypeError()
                componentsschemas_change_diagram_outcome_type_3 = cast(Literal["OVER_CAPS"], data)
                if componentsschemas_change_diagram_outcome_type_3 != "OVER_CAPS":
                    raise ValueError(
                        f"/components/schemas/ChangeDiagramOutcome_type_3 must match const 'OVER_CAPS', got '{componentsschemas_change_diagram_outcome_type_3}'"
                    )
                return componentsschemas_change_diagram_outcome_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "DECISION_UNAVAILABLE"):
                raise TypeError()
            componentsschemas_change_diagram_outcome_type_4 = cast(
                Literal["DECISION_UNAVAILABLE"], data
            )
            if componentsschemas_change_diagram_outcome_type_4 != "DECISION_UNAVAILABLE":
                raise ValueError(
                    f"/components/schemas/ChangeDiagramOutcome_type_4 must match const 'DECISION_UNAVAILABLE', got '{componentsschemas_change_diagram_outcome_type_4}'"
                )
            return componentsschemas_change_diagram_outcome_type_4

        outcome = _parse_outcome(d.pop("outcome"))

        def _parse_kind(data: object) -> ChangeDiagramKindView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                kind_type_0 = ChangeDiagramKindView(data)

                return kind_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChangeDiagramKindView | None | Unset, data)

        kind = _parse_kind(d.pop("kind", UNSET))

        def _parse_mermaid(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mermaid = _parse_mermaid(d.pop("mermaid", UNSET))

        change_diagram_view = cls(
            legend=legend,
            outcome=outcome,
            kind=kind,
            mermaid=mermaid,
        )

        change_diagram_view.additional_properties = d
        return change_diagram_view

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
