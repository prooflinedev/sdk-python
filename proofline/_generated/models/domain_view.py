from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DomainView")


@_attrs_define
class DomainView:
    """
    Attributes:
        domain (str): The risk domain this evaluation covers.
        reason (str): Why the domain was considered or skipped, as recorded with the evaluation.
        status (str): `CONSIDERED` or `SKIPPED`.
    """

    domain: str
    reason: str
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain = self.domain

        reason = self.reason

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain": domain,
                "reason": reason,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domain = d.pop("domain")

        reason = d.pop("reason")

        status = d.pop("status")

        domain_view = cls(
            domain=domain,
            reason=reason,
            status=status,
        )

        domain_view.additional_properties = d
        return domain_view

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
