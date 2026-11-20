from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReviewCostFunding")


@_attrs_define
class ReviewCostFunding:
    """What paid for a run's credit cost, as Usage splits a day. The three parts
    add up to the cost.

       Attributes:
           free_review_microcredits (int): Paid by the free review month: the same organization's
                `free-review:{debit_id}` grants for the run's debits.
           organization_microcredits (int): Taken from the organization's shared credit balance.
           plan_microcredits (int): Paid by the workspace allowance or the author's seat.
    """

    free_review_microcredits: int
    organization_microcredits: int
    plan_microcredits: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        free_review_microcredits = self.free_review_microcredits

        organization_microcredits = self.organization_microcredits

        plan_microcredits = self.plan_microcredits

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "free_review_microcredits": free_review_microcredits,
                "organization_microcredits": organization_microcredits,
                "plan_microcredits": plan_microcredits,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        free_review_microcredits = d.pop("free_review_microcredits")

        organization_microcredits = d.pop("organization_microcredits")

        plan_microcredits = d.pop("plan_microcredits")

        review_cost_funding = cls(
            free_review_microcredits=free_review_microcredits,
            organization_microcredits=organization_microcredits,
            plan_microcredits=plan_microcredits,
        )

        review_cost_funding.additional_properties = d
        return review_cost_funding

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
