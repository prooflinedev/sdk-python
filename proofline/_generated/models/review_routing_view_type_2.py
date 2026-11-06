from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.plan_projection import PlanProjection
    from ..models.routing_finding_view import RoutingFindingView


T = TypeVar("T", bound="ReviewRoutingViewType2")


@_attrs_define
class ReviewRoutingViewType2:
    """Validated routing and placement facts for this review.

    Attributes:
        findings (list[RoutingFindingView]): Recorded publication decisions, with unrecognized codes masked.
        plan (PlanProjection):
        status (Literal['SUPPORTED']):
        version (str): Version of the validated routing plan.
    """

    findings: list[RoutingFindingView]
    plan: PlanProjection
    status: Literal["SUPPORTED"]
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        findings = []
        for findings_item_data in self.findings:
            findings_item = findings_item_data.to_dict()
            findings.append(findings_item)

        plan = self.plan.to_dict()

        status = self.status

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "findings": findings,
                "plan": plan,
                "status": status,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_projection import PlanProjection  # noqa: PLC0415
        from ..models.routing_finding_view import RoutingFindingView  # noqa: PLC0415

        d = dict(src_dict)
        findings = []
        _findings = d.pop("findings")
        for findings_item_data in _findings:
            findings_item = RoutingFindingView.from_dict(findings_item_data)

            findings.append(findings_item)

        plan = PlanProjection.from_dict(d.pop("plan"))

        status = cast(Literal["SUPPORTED"], d.pop("status"))
        if status != "SUPPORTED":
            raise ValueError(f"status must match const 'SUPPORTED', got '{status}'")

        version = d.pop("version")

        review_routing_view_type_2 = cls(
            findings=findings,
            plan=plan,
            status=status,
            version=version,
        )

        review_routing_view_type_2.additional_properties = d
        return review_routing_view_type_2

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
