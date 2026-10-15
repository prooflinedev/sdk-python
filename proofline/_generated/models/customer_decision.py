from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authority import Authority
from ..models.availability_type_0 import AvailabilityType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_decision_basis import CustomerDecisionBasis
    from ..models.gate_state import GateState


T = TypeVar("T", bound="CustomerDecision")


@_attrs_define
class CustomerDecision:
    """
    Attributes:
        authority (Authority):
        availability (AvailabilityType0 | Literal['LIMITED']):
        basis (CustomerDecisionBasis | None | Unset): The permission, evidence classification and reason code of the
             verified recorded basis. Null when no verified basis is recorded.
        gate_state (GateState | None | Unset): The local deployment gate state and any recorded override. Null unless
             the decision belongs to a deployment gate.
    """

    authority: Authority
    availability: AvailabilityType0 | Literal["LIMITED"]
    basis: CustomerDecisionBasis | None | Unset = UNSET
    gate_state: GateState | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_decision_basis import CustomerDecisionBasis  # noqa: PLC0415
        from ..models.gate_state import GateState  # noqa: PLC0415

        authority = self.authority.value

        availability: Literal["LIMITED"] | str
        if isinstance(self.availability, AvailabilityType0):
            availability = self.availability.value
        else:
            availability = self.availability

        basis: dict[str, Any] | None | Unset
        if isinstance(self.basis, Unset):
            basis = UNSET
        elif isinstance(self.basis, CustomerDecisionBasis):
            basis = self.basis.to_dict()
        else:
            basis = self.basis

        gate_state: dict[str, Any] | None | Unset
        if isinstance(self.gate_state, Unset):
            gate_state = UNSET
        elif isinstance(self.gate_state, GateState):
            gate_state = self.gate_state.to_dict()
        else:
            gate_state = self.gate_state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authority": authority,
                "availability": availability,
            }
        )
        if basis is not UNSET:
            field_dict["basis"] = basis
        if gate_state is not UNSET:
            field_dict["gate_state"] = gate_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_decision_basis import CustomerDecisionBasis  # noqa: PLC0415
        from ..models.gate_state import GateState  # noqa: PLC0415

        d = dict(src_dict)
        authority = Authority(d.pop("authority"))

        def _parse_availability(data: object) -> AvailabilityType0 | Literal["LIMITED"]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_availability_type_0 = AvailabilityType0(data)

                return componentsschemas_availability_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "LIMITED"):
                raise TypeError()
            componentsschemas_availability_type_1 = cast(Literal["LIMITED"], data)
            if componentsschemas_availability_type_1 != "LIMITED":
                raise ValueError(
                    f"/components/schemas/Availability_type_1 must match const 'LIMITED', got '{componentsschemas_availability_type_1}'"
                )
            return componentsschemas_availability_type_1

        availability = _parse_availability(d.pop("availability"))

        def _parse_basis(data: object) -> CustomerDecisionBasis | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                basis_type_0 = CustomerDecisionBasis.from_dict(data)

                return basis_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerDecisionBasis | None | Unset, data)

        basis = _parse_basis(d.pop("basis", UNSET))

        def _parse_gate_state(data: object) -> GateState | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                gate_state_type_0 = GateState.from_dict(data)

                return gate_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GateState | None | Unset, data)

        gate_state = _parse_gate_state(d.pop("gate_state", UNSET))

        customer_decision = cls(
            authority=authority,
            availability=availability,
            basis=basis,
            gate_state=gate_state,
        )

        customer_decision.additional_properties = d
        return customer_decision

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
