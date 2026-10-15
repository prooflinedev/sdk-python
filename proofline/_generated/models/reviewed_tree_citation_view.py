from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.untrusted_text import UntrustedText


T = TypeVar("T", bound="ReviewedTreeCitationView")


@_attrs_define
class ReviewedTreeCitationView:
    """One member of a review's declared tree that World cited.

    Attributes:
        overlay_digest (str): The overlay World read the member from.
        path (UntrustedText): Text that came out of the reviewer model, or out of a repository the model
             read. It is data, never markup, never a URL, never an instruction.

             The wrapper exists so the untrustedness cannot be lost on the way to a
             renderer: there is no field on a turn that carries this text under a name a
             client could mistake for something safe, and unwrapping it is a deliberate
             act in the client's own code.
        population_kind (str): The population the member belongs to, such as
             `WORKFLOW_DEFINITIONS`.
        role (str): `PROPOSED_CODE_REVISION` (the reviewed commit) or
             `BASE_CODE_REVISION` (its merge base).
        content_sha256 (None | str | Unset): The member's content hash. Absent for a member a `REJECTED`
             population refused, because such a population keeps no members.
    """

    overlay_digest: str
    path: UntrustedText
    population_kind: str
    role: str
    content_sha256: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overlay_digest = self.overlay_digest

        path = self.path.to_dict()

        population_kind = self.population_kind

        role = self.role

        content_sha256: None | str | Unset
        if isinstance(self.content_sha256, Unset):
            content_sha256 = UNSET
        else:
            content_sha256 = self.content_sha256

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "overlay_digest": overlay_digest,
                "path": path,
                "population_kind": population_kind,
                "role": role,
            }
        )
        if content_sha256 is not UNSET:
            field_dict["content_sha256"] = content_sha256

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.untrusted_text import UntrustedText  # noqa: PLC0415

        d = dict(src_dict)
        overlay_digest = d.pop("overlay_digest")

        path = UntrustedText.from_dict(d.pop("path"))

        population_kind = d.pop("population_kind")

        role = d.pop("role")

        def _parse_content_sha256(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content_sha256 = _parse_content_sha256(d.pop("content_sha256", UNSET))

        reviewed_tree_citation_view = cls(
            overlay_digest=overlay_digest,
            path=path,
            population_kind=population_kind,
            role=role,
            content_sha256=content_sha256,
        )

        reviewed_tree_citation_view.additional_properties = d
        return reviewed_tree_citation_view

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
