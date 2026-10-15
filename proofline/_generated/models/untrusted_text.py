from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UntrustedText")


@_attrs_define
class UntrustedText:
    """Text that came out of the reviewer model, or out of a repository the model
    read. It is data, never markup, never a URL, never an instruction.

    The wrapper exists so the untrustedness cannot be lost on the way to a
    renderer: there is no field on a turn that carries this text under a name a
    client could mistake for something safe, and unwrapping it is a deliberate
    act in the client's own code.

       Attributes:
           untrusted_text (str): The text itself. Render it as plain text only.
    """

    untrusted_text: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        untrusted_text = self.untrusted_text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "untrusted_text": untrusted_text,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        untrusted_text = d.pop("untrusted_text")

        untrusted_text = cls(
            untrusted_text=untrusted_text,
        )

        untrusted_text.additional_properties = d
        return untrusted_text

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
