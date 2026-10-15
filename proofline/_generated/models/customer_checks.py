from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.customer_check import CustomerCheck


T = TypeVar("T", bound="CustomerChecks")


@_attrs_define
class CustomerChecks:
    """
    Attributes:
        families (list[CustomerCheck]): One entry per recorded check result, ordered by check key and version.
             Empty when no receipt exists.
        receipt_recorded (bool): Whether these checks come from an immutable deterministic coverage
             receipt. When false, no check result is recorded.
        status (str): The receipt's status, or `PENDING`, `SUPERSEDED`, `STOPPED`,
             `NOT_ATTEMPTED` or `UNAVAILABLE` when no receipt exists.
    """

    families: list[CustomerCheck]
    receipt_recorded: bool
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        families = []
        for families_item_data in self.families:
            families_item = families_item_data.to_dict()
            families.append(families_item)

        receipt_recorded = self.receipt_recorded

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "families": families,
                "receipt_recorded": receipt_recorded,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_check import CustomerCheck  # noqa: PLC0415

        d = dict(src_dict)
        families = []
        _families = d.pop("families")
        for families_item_data in _families:
            families_item = CustomerCheck.from_dict(families_item_data)

            families.append(families_item)

        receipt_recorded = d.pop("receipt_recorded")

        status = d.pop("status")

        customer_checks = cls(
            families=families,
            receipt_recorded=receipt_recorded,
            status=status,
        )

        customer_checks.additional_properties = d
        return customer_checks

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
