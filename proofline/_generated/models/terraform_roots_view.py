from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.terraform_plan_view import TerraformPlanView

T = TypeVar("T", bound="TerraformRootsView")


@_attrs_define
class TerraformRootsView:
    """The Terraform roots of one declared reach read.

    Attributes:
        addresses (list[str]): The changed resource instance addresses taken as roots.
        omitted (int): Changed addresses left out at World's limit of 100 roots per read.
        plan (TerraformPlanView):
    """

    addresses: list[str]
    omitted: int
    plan: TerraformPlanView
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        addresses = self.addresses

        omitted = self.omitted

        plan = self.plan.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "addresses": addresses,
                "omitted": omitted,
                "plan": plan,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        addresses = cast(list[str], d.pop("addresses"))

        omitted = d.pop("omitted")

        plan = TerraformPlanView(d.pop("plan"))

        terraform_roots_view = cls(
            addresses=addresses,
            omitted=omitted,
            plan=plan,
        )

        terraform_roots_view.additional_properties = d
        return terraform_roots_view

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
