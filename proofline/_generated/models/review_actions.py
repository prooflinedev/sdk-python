from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.action_unavailability import ActionUnavailability
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReviewActions")


@_attrs_define
class ReviewActions:
    """
    Attributes:
        promote_findings (bool): Whether a browser caller may request publication of a routed finding.
        publish (bool): Whether the caller may publish this pull request review's withheld
             results, which requires a browser session and repository write access.
        rerun (bool): Whether the caller may rerun this review.
        stop (bool): Whether the caller may stop this review from a browser session.
        validate_findings (bool): Whether the caller may record decisions on findings from a browser
             session.
        unavailable_reason (ActionUnavailability | None | Unset): Why an action is unavailable, when a permission or
            repository check
             denied it. Null when no check denied one, which does not mean every
             action is allowed.
    """

    promote_findings: bool
    publish: bool
    rerun: bool
    stop: bool
    validate_findings: bool
    unavailable_reason: ActionUnavailability | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        promote_findings = self.promote_findings

        publish = self.publish

        rerun = self.rerun

        stop = self.stop

        validate_findings = self.validate_findings

        unavailable_reason: None | str | Unset
        if isinstance(self.unavailable_reason, Unset):
            unavailable_reason = UNSET
        elif isinstance(self.unavailable_reason, ActionUnavailability):
            unavailable_reason = self.unavailable_reason.value
        else:
            unavailable_reason = self.unavailable_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "promote_findings": promote_findings,
                "publish": publish,
                "rerun": rerun,
                "stop": stop,
                "validate_findings": validate_findings,
            }
        )
        if unavailable_reason is not UNSET:
            field_dict["unavailable_reason"] = unavailable_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        promote_findings = d.pop("promote_findings")

        publish = d.pop("publish")

        rerun = d.pop("rerun")

        stop = d.pop("stop")

        validate_findings = d.pop("validate_findings")

        def _parse_unavailable_reason(data: object) -> ActionUnavailability | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                unavailable_reason_type_0 = ActionUnavailability(data)

                return unavailable_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActionUnavailability | None | Unset, data)

        unavailable_reason = _parse_unavailable_reason(d.pop("unavailable_reason", UNSET))

        review_actions = cls(
            promote_findings=promote_findings,
            publish=publish,
            rerun=rerun,
            stop=stop,
            validate_findings=validate_findings,
            unavailable_reason=unavailable_reason,
        )

        review_actions.additional_properties = d
        return review_actions

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
