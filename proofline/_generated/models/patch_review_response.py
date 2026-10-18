from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.patch_verification import PatchVerification


T = TypeVar("T", bound="PatchReviewResponse")


@_attrs_define
class PatchReviewResponse:
    """What a patch review request produced.

    Attributes:
        existing (bool): True when this patch on this base already had a review and that one
             is returned. Sending the same patch twice reviews it once.
        patch_digest (str): SHA-256 of the canonical patch, the identity the review pins with
             the repository and base commit.
        review_id (UUID): The review of this patch on this base, readable through the review
             and findings routes.
        verify (list[PatchVerification]): Each finding of `verify_finding_ids` the review re-verifies, one per
             finding series. Empty without `verify_finding_ids`.
    """

    existing: bool
    patch_digest: str
    review_id: UUID
    verify: list[PatchVerification]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        existing = self.existing

        patch_digest = self.patch_digest

        review_id = str(self.review_id)

        verify = []
        for verify_item_data in self.verify:
            verify_item = verify_item_data.to_dict()
            verify.append(verify_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "existing": existing,
                "patch_digest": patch_digest,
                "review_id": review_id,
                "verify": verify,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.patch_verification import PatchVerification  # noqa: PLC0415

        d = dict(src_dict)
        existing = d.pop("existing")

        patch_digest = d.pop("patch_digest")

        review_id = UUID(d.pop("review_id"))

        verify = []
        _verify = d.pop("verify")
        for verify_item_data in _verify:
            verify_item = PatchVerification.from_dict(verify_item_data)

            verify.append(verify_item)

        patch_review_response = cls(
            existing=existing,
            patch_digest=patch_digest,
            review_id=review_id,
            verify=verify,
        )

        patch_review_response.additional_properties = d
        return patch_review_response

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
