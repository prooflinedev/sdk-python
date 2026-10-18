from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PatchVerification")


@_attrs_define
class PatchVerification:
    """One finding a patch review re-verifies against the patch.

    Attributes:
        finding_id (UUID):
        iteration (int): This request's number among the requests to re-verify the finding's
             series on this patch, at most 3.
    """

    finding_id: UUID
    iteration: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        finding_id = str(self.finding_id)

        iteration = self.iteration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "finding_id": finding_id,
                "iteration": iteration,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        finding_id = UUID(d.pop("finding_id"))

        iteration = d.pop("iteration")

        patch_verification = cls(
            finding_id=finding_id,
            iteration=iteration,
        )

        patch_verification.additional_properties = d
        return patch_verification

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
