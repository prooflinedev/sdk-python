from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.untrusted_text import UntrustedText


T = TypeVar("T", bound="CheckFile")


@_attrs_define
class CheckFile:
    """One file World cited for a check's result.

    Attributes:
        path (UntrustedText): Text that came out of the reviewer model, or out of a repository the model
             read. It is data, never markup, never a URL, never an instruction.

             The wrapper exists so the untrustedness cannot be lost on the way to a
             renderer: there is no field on a turn that carries this text under a name a
             client could mistake for something safe, and unwrapping it is a deliberate
             act in the client's own code.
        revision (Literal['BASE_CODE_REVISION'] | Literal['PROPOSED_CODE_REVISION']): The revision a cited file was read
            at.
    """

    path: UntrustedText
    revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path.to_dict()

        revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "revision": revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.untrusted_text import UntrustedText  # noqa: PLC0415

        d = dict(src_dict)
        path = UntrustedText.from_dict(d.pop("path"))

        def _parse_revision(
            data: object,
        ) -> Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]:
            try:
                if not (type(data) is str and data == "PROPOSED_CODE_REVISION"):
                    raise TypeError()
                componentsschemas_check_file_revision_type_0 = cast(
                    Literal["PROPOSED_CODE_REVISION"], data
                )
                if componentsschemas_check_file_revision_type_0 != "PROPOSED_CODE_REVISION":
                    raise ValueError(
                        f"/components/schemas/CheckFileRevision_type_0 must match const 'PROPOSED_CODE_REVISION', got '{componentsschemas_check_file_revision_type_0}'"
                    )
                return componentsschemas_check_file_revision_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "BASE_CODE_REVISION"):
                raise TypeError()
            componentsschemas_check_file_revision_type_1 = cast(Literal["BASE_CODE_REVISION"], data)
            if componentsschemas_check_file_revision_type_1 != "BASE_CODE_REVISION":
                raise ValueError(
                    f"/components/schemas/CheckFileRevision_type_1 must match const 'BASE_CODE_REVISION', got '{componentsschemas_check_file_revision_type_1}'"
                )
            return componentsschemas_check_file_revision_type_1

        revision = _parse_revision(d.pop("revision"))

        check_file = cls(
            path=path,
            revision=revision,
        )

        check_file.additional_properties = d
        return check_file

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
