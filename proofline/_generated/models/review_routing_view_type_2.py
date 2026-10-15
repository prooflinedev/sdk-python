from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plan_projection import PlanProjection
    from ..models.routing_finding_view import RoutingFindingView
    from ..models.specialist_execution_view import SpecialistExecutionView


T = TypeVar("T", bound="ReviewRoutingViewType2")


@_attrs_define
class ReviewRoutingViewType2:
    """Validated routing and placement facts for this review.

    Attributes:
        findings (list[RoutingFindingView]): Recorded publication decisions, with unrecognized codes masked.
        plan (PlanProjection):
        status (Literal['SUPPORTED']):
        version (str): Version of the validated routing plan.
        specialist_execution (None | SpecialistExecutionView | Unset): Actual specialist selection and pass receipts for
            the applied workflow.
    """

    findings: list[RoutingFindingView]
    plan: PlanProjection
    status: Literal["SUPPORTED"]
    version: str
    specialist_execution: None | SpecialistExecutionView | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.specialist_execution_view import SpecialistExecutionView  # noqa: PLC0415

        findings = []
        for findings_item_data in self.findings:
            findings_item = findings_item_data.to_dict()
            findings.append(findings_item)

        plan = self.plan.to_dict()

        status = self.status

        version = self.version

        specialist_execution: dict[str, Any] | None | Unset
        if isinstance(self.specialist_execution, Unset):
            specialist_execution = UNSET
        elif isinstance(self.specialist_execution, SpecialistExecutionView):
            specialist_execution = self.specialist_execution.to_dict()
        else:
            specialist_execution = self.specialist_execution

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
        if specialist_execution is not UNSET:
            field_dict["specialist_execution"] = specialist_execution

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_projection import PlanProjection  # noqa: PLC0415
        from ..models.routing_finding_view import RoutingFindingView  # noqa: PLC0415
        from ..models.specialist_execution_view import SpecialistExecutionView  # noqa: PLC0415

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

        def _parse_specialist_execution(data: object) -> None | SpecialistExecutionView | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                specialist_execution_type_0 = SpecialistExecutionView.from_dict(data)

                return specialist_execution_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SpecialistExecutionView | Unset, data)

        specialist_execution = _parse_specialist_execution(d.pop("specialist_execution", UNSET))

        review_routing_view_type_2 = cls(
            findings=findings,
            plan=plan,
            status=status,
            version=version,
            specialist_execution=specialist_execution,
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
