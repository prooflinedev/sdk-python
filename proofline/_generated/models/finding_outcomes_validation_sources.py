from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FindingOutcomesValidationSources")


@_attrs_define
class FindingOutcomesValidationSources:
    """
    Attributes:
        console (int): Series whose outcome comes from a validation recorded in the console.
        github_reply (int): Series whose outcome comes from a validation recorded by a GitHub comment reply.
        proofline (int): Series whose outcome is `ALREADY_COVERED`, recorded by Proofline itself.
    """

    console: int
    github_reply: int
    proofline: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        console = self.console

        github_reply = self.github_reply

        proofline = self.proofline

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "console": console,
                "github_reply": github_reply,
                "proofline": proofline,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        console = d.pop("console")

        github_reply = d.pop("github_reply")

        proofline = d.pop("proofline")

        finding_outcomes_validation_sources = cls(
            console=console,
            github_reply=github_reply,
            proofline=proofline,
        )

        finding_outcomes_validation_sources.additional_properties = d
        return finding_outcomes_validation_sources

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
