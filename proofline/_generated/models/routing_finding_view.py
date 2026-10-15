from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.finding_promotion_view import FindingPromotionView


T = TypeVar("T", bound="RoutingFindingView")


@_attrs_define
class RoutingFindingView:
    """
    Attributes:
        finding_id (UUID): Finding whose retained placement is reported.
        inline_limit_exceeded (bool): The original inline choice exceeded this review's inline comment limit.
        placement (str): Publication channel recorded for this finding.
        reason_codes (list[str]): Recognized safe reason codes; unknown values are represented as `UNRECOGNIZED`.
        rule (str): Rule that produced the recorded placement.
        fallback_cause (None | str | Unset): Recognized safe fallback cause, when present.
        floor_reason (None | str | Unset): Recognized safe floor reason, when present.
        inline_reason (None | str | Unset): Why the recorded publication did not create an inline comment, when
            retained.
        promotion (FindingPromotionView | None | Unset): Human override beside the original decision, when one was
            requested.
    """

    finding_id: UUID
    inline_limit_exceeded: bool
    placement: str
    reason_codes: list[str]
    rule: str
    fallback_cause: None | str | Unset = UNSET
    floor_reason: None | str | Unset = UNSET
    inline_reason: None | str | Unset = UNSET
    promotion: FindingPromotionView | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.finding_promotion_view import FindingPromotionView  # noqa: PLC0415

        finding_id = str(self.finding_id)

        inline_limit_exceeded = self.inline_limit_exceeded

        placement = self.placement

        reason_codes = self.reason_codes

        rule = self.rule

        fallback_cause: None | str | Unset
        if isinstance(self.fallback_cause, Unset):
            fallback_cause = UNSET
        else:
            fallback_cause = self.fallback_cause

        floor_reason: None | str | Unset
        if isinstance(self.floor_reason, Unset):
            floor_reason = UNSET
        else:
            floor_reason = self.floor_reason

        inline_reason: None | str | Unset
        if isinstance(self.inline_reason, Unset):
            inline_reason = UNSET
        else:
            inline_reason = self.inline_reason

        promotion: dict[str, Any] | None | Unset
        if isinstance(self.promotion, Unset):
            promotion = UNSET
        elif isinstance(self.promotion, FindingPromotionView):
            promotion = self.promotion.to_dict()
        else:
            promotion = self.promotion

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "finding_id": finding_id,
                "inline_limit_exceeded": inline_limit_exceeded,
                "placement": placement,
                "reason_codes": reason_codes,
                "rule": rule,
            }
        )
        if fallback_cause is not UNSET:
            field_dict["fallback_cause"] = fallback_cause
        if floor_reason is not UNSET:
            field_dict["floor_reason"] = floor_reason
        if inline_reason is not UNSET:
            field_dict["inline_reason"] = inline_reason
        if promotion is not UNSET:
            field_dict["promotion"] = promotion

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finding_promotion_view import FindingPromotionView  # noqa: PLC0415

        d = dict(src_dict)
        finding_id = UUID(d.pop("finding_id"))

        inline_limit_exceeded = d.pop("inline_limit_exceeded")

        placement = d.pop("placement")

        reason_codes = cast(list[str], d.pop("reason_codes"))

        rule = d.pop("rule")

        def _parse_fallback_cause(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        fallback_cause = _parse_fallback_cause(d.pop("fallback_cause", UNSET))

        def _parse_floor_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        floor_reason = _parse_floor_reason(d.pop("floor_reason", UNSET))

        def _parse_inline_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        inline_reason = _parse_inline_reason(d.pop("inline_reason", UNSET))

        def _parse_promotion(data: object) -> FindingPromotionView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                promotion_type_0 = FindingPromotionView.from_dict(data)

                return promotion_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingPromotionView | None | Unset, data)

        promotion = _parse_promotion(d.pop("promotion", UNSET))

        routing_finding_view = cls(
            finding_id=finding_id,
            inline_limit_exceeded=inline_limit_exceeded,
            placement=placement,
            reason_codes=reason_codes,
            rule=rule,
            fallback_cause=fallback_cause,
            floor_reason=floor_reason,
            inline_reason=inline_reason,
            promotion=promotion,
        )

        routing_finding_view.additional_properties = d
        return routing_finding_view

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
