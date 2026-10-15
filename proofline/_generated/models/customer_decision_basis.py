from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.evidence_view import EvidenceView
from ..models.permission_view import PermissionView

T = TypeVar("T", bound="CustomerDecisionBasis")


@_attrs_define
class CustomerDecisionBasis:
    """
    Attributes:
        evidence (EvidenceView):
        permission (PermissionView):
        reason_code (str): The reason code the recorded basis gives for its permission.
    """

    evidence: EvidenceView
    permission: PermissionView
    reason_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        evidence = self.evidence.value

        permission = self.permission.value

        reason_code = self.reason_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "evidence": evidence,
                "permission": permission,
                "reason_code": reason_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        evidence = EvidenceView(d.pop("evidence"))

        permission = PermissionView(d.pop("permission"))

        reason_code = d.pop("reason_code")

        customer_decision_basis = cls(
            evidence=evidence,
            permission=permission,
            reason_code=reason_code,
        )

        customer_decision_basis.additional_properties = d
        return customer_decision_basis

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
