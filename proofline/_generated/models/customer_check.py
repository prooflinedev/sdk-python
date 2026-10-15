from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.change_attribution_view import ChangeAttributionView


T = TypeVar("T", bound="CustomerCheck")


@_attrs_define
class CustomerCheck:
    """
    Attributes:
        lifecycle (Literal['GATING'] | Literal['QUARANTINED'] | Literal['RETIRED'] | Literal['SHADOW'] |
            Literal['UNKNOWN']): World's lifecycle disclosure for the evaluator version that answered, as
             the receipt recorded it. A deployment gate counts only `GATING` results
             (`DeterministicCoverage::gate_effective_status`), and only when it
             evaluates a deployment; the lifecycle alone permits or blocks nothing.
        name (str): The check's readable name, derived from its key.
        outcome (str): The outcome the receipt recorded, which is the outcome a deployment
             gate weighed: `READY`, `BLOCKED`, `UNRESOLVED`, `UNAVAILABLE`,
             `NOT_APPLICABLE` or `NOT_ASKED`. A verdict never rewrites it.
        change_attribution (ChangeAttributionView | None | Unset): Which conditions behind the outcome the change
            brought and which were
             already at the review's base revision. It never changes the outcome:
             a condition already at the base is pre-existing, not safe. Absent for
             a check whose evaluator does not compare the two revisions.
        detail (None | str | Unset): Why World refused the check, or otherwise World's recorded explanation
             of the result. Null when neither is recorded.
        evaluated_at (None | str | Unset): When World evaluated this answer. A reused answer is evidence from
             this instant, which can precede the assessment.
        unresolved_reason (Literal['NEEDS_EVIDENCE'] | Literal['REGENERATE_SCENARIO'] | Literal['UNSUPPORTED'] | None |
            Unset): Why an `UNRESOLVED` check did not settle, as World's verdict gave it.
             Absent on every other outcome, and on an unresolved receipt whose
             verdict names none of these reasons.
    """

    lifecycle: (
        Literal["GATING"]
        | Literal["QUARANTINED"]
        | Literal["RETIRED"]
        | Literal["SHADOW"]
        | Literal["UNKNOWN"]
    )
    name: str
    outcome: str
    change_attribution: ChangeAttributionView | None | Unset = UNSET
    detail: None | str | Unset = UNSET
    evaluated_at: None | str | Unset = UNSET
    unresolved_reason: (
        Literal["NEEDS_EVIDENCE"]
        | Literal["REGENERATE_SCENARIO"]
        | Literal["UNSUPPORTED"]
        | None
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.change_attribution_view import ChangeAttributionView  # noqa: PLC0415

        lifecycle: (
            Literal["GATING"]
            | Literal["QUARANTINED"]
            | Literal["RETIRED"]
            | Literal["SHADOW"]
            | Literal["UNKNOWN"]
        )
        lifecycle = self.lifecycle

        name = self.name

        outcome = self.outcome

        change_attribution: dict[str, Any] | None | Unset
        if isinstance(self.change_attribution, Unset):
            change_attribution = UNSET
        elif isinstance(self.change_attribution, ChangeAttributionView):
            change_attribution = self.change_attribution.to_dict()
        else:
            change_attribution = self.change_attribution

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        evaluated_at: None | str | Unset
        if isinstance(self.evaluated_at, Unset):
            evaluated_at = UNSET
        else:
            evaluated_at = self.evaluated_at

        unresolved_reason: (
            Literal["NEEDS_EVIDENCE"]
            | Literal["REGENERATE_SCENARIO"]
            | Literal["UNSUPPORTED"]
            | None
            | Unset
        )
        if isinstance(self.unresolved_reason, Unset):
            unresolved_reason = UNSET
        else:
            unresolved_reason = self.unresolved_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "lifecycle": lifecycle,
                "name": name,
                "outcome": outcome,
            }
        )
        if change_attribution is not UNSET:
            field_dict["change_attribution"] = change_attribution
        if detail is not UNSET:
            field_dict["detail"] = detail
        if evaluated_at is not UNSET:
            field_dict["evaluated_at"] = evaluated_at
        if unresolved_reason is not UNSET:
            field_dict["unresolved_reason"] = unresolved_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.change_attribution_view import ChangeAttributionView  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_lifecycle(
            data: object,
        ) -> (
            Literal["GATING"]
            | Literal["QUARANTINED"]
            | Literal["RETIRED"]
            | Literal["SHADOW"]
            | Literal["UNKNOWN"]
        ):
            try:
                if not (type(data) is str and data == "GATING"):
                    raise TypeError()
                componentsschemas_check_lifecycle_type_0 = cast(Literal["GATING"], data)
                if componentsschemas_check_lifecycle_type_0 != "GATING":
                    raise ValueError(
                        f"/components/schemas/CheckLifecycle_type_0 must match const 'GATING', got '{componentsschemas_check_lifecycle_type_0}'"
                    )
                return componentsschemas_check_lifecycle_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "SHADOW"):
                    raise TypeError()
                componentsschemas_check_lifecycle_type_1 = cast(Literal["SHADOW"], data)
                if componentsschemas_check_lifecycle_type_1 != "SHADOW":
                    raise ValueError(
                        f"/components/schemas/CheckLifecycle_type_1 must match const 'SHADOW', got '{componentsschemas_check_lifecycle_type_1}'"
                    )
                return componentsschemas_check_lifecycle_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "QUARANTINED"):
                    raise TypeError()
                componentsschemas_check_lifecycle_type_2 = cast(Literal["QUARANTINED"], data)
                if componentsschemas_check_lifecycle_type_2 != "QUARANTINED":
                    raise ValueError(
                        f"/components/schemas/CheckLifecycle_type_2 must match const 'QUARANTINED', got '{componentsschemas_check_lifecycle_type_2}'"
                    )
                return componentsschemas_check_lifecycle_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "RETIRED"):
                    raise TypeError()
                componentsschemas_check_lifecycle_type_3 = cast(Literal["RETIRED"], data)
                if componentsschemas_check_lifecycle_type_3 != "RETIRED":
                    raise ValueError(
                        f"/components/schemas/CheckLifecycle_type_3 must match const 'RETIRED', got '{componentsschemas_check_lifecycle_type_3}'"
                    )
                return componentsschemas_check_lifecycle_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "UNKNOWN"):
                raise TypeError()
            componentsschemas_check_lifecycle_type_4 = cast(Literal["UNKNOWN"], data)
            if componentsschemas_check_lifecycle_type_4 != "UNKNOWN":
                raise ValueError(
                    f"/components/schemas/CheckLifecycle_type_4 must match const 'UNKNOWN', got '{componentsschemas_check_lifecycle_type_4}'"
                )
            return componentsschemas_check_lifecycle_type_4

        lifecycle = _parse_lifecycle(d.pop("lifecycle"))

        name = d.pop("name")

        outcome = d.pop("outcome")

        def _parse_change_attribution(data: object) -> ChangeAttributionView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                change_attribution_type_0 = ChangeAttributionView.from_dict(data)

                return change_attribution_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChangeAttributionView | None | Unset, data)

        change_attribution = _parse_change_attribution(d.pop("change_attribution", UNSET))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        def _parse_evaluated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        evaluated_at = _parse_evaluated_at(d.pop("evaluated_at", UNSET))

        def _parse_unresolved_reason(
            data: object,
        ) -> (
            Literal["NEEDS_EVIDENCE"]
            | Literal["REGENERATE_SCENARIO"]
            | Literal["UNSUPPORTED"]
            | None
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not (type(data) is str and data == "NEEDS_EVIDENCE"):
                    raise TypeError()
                componentsschemas_unresolved_reason_type_0 = cast(Literal["NEEDS_EVIDENCE"], data)
                if componentsschemas_unresolved_reason_type_0 != "NEEDS_EVIDENCE":
                    raise ValueError(
                        f"/components/schemas/UnresolvedReason_type_0 must match const 'NEEDS_EVIDENCE', got '{componentsschemas_unresolved_reason_type_0}'"
                    )
                return componentsschemas_unresolved_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNSUPPORTED"):
                    raise TypeError()
                componentsschemas_unresolved_reason_type_1 = cast(Literal["UNSUPPORTED"], data)
                if componentsschemas_unresolved_reason_type_1 != "UNSUPPORTED":
                    raise ValueError(
                        f"/components/schemas/UnresolvedReason_type_1 must match const 'UNSUPPORTED', got '{componentsschemas_unresolved_reason_type_1}'"
                    )
                return componentsschemas_unresolved_reason_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "REGENERATE_SCENARIO"):
                    raise TypeError()
                componentsschemas_unresolved_reason_type_2 = cast(
                    Literal["REGENERATE_SCENARIO"], data
                )
                if componentsschemas_unresolved_reason_type_2 != "REGENERATE_SCENARIO":
                    raise ValueError(
                        f"/components/schemas/UnresolvedReason_type_2 must match const 'REGENERATE_SCENARIO', got '{componentsschemas_unresolved_reason_type_2}'"
                    )
                return componentsschemas_unresolved_reason_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["NEEDS_EVIDENCE"]
                | Literal["REGENERATE_SCENARIO"]
                | Literal["UNSUPPORTED"]
                | None
                | Unset,
                data,
            )

        unresolved_reason = _parse_unresolved_reason(d.pop("unresolved_reason", UNSET))

        customer_check = cls(
            lifecycle=lifecycle,
            name=name,
            outcome=outcome,
            change_attribution=change_attribution,
            detail=detail,
            evaluated_at=evaluated_at,
            unresolved_reason=unresolved_reason,
        )

        customer_check.additional_properties = d
        return customer_check

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
