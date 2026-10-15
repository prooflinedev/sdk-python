from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.customer_evidence_ref import CustomerEvidenceRef
    from ..models.untrusted_text import UntrustedText


T = TypeVar("T", bound="FindingSupport")


@_attrs_define
class FindingSupport:
    """
    Attributes:
        evidence_refs (list[CustomerEvidenceRef]): The references the hypothesis cites for its verdict.
        explanation (None | Unset | UntrustedText): Why the hypothesis reached its verdict, as recorded at resolution.
            Null
             when no explanation is recorded.
    """

    evidence_refs: list[CustomerEvidenceRef]
    explanation: None | Unset | UntrustedText = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.untrusted_text import UntrustedText  # noqa: PLC0415

        evidence_refs = []
        for evidence_refs_item_data in self.evidence_refs:
            evidence_refs_item = evidence_refs_item_data.to_dict()
            evidence_refs.append(evidence_refs_item)

        explanation: dict[str, Any] | None | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        elif isinstance(self.explanation, UntrustedText):
            explanation = self.explanation.to_dict()
        else:
            explanation = self.explanation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "evidence_refs": evidence_refs,
            }
        )
        if explanation is not UNSET:
            field_dict["explanation"] = explanation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_evidence_ref import CustomerEvidenceRef  # noqa: PLC0415
        from ..models.untrusted_text import UntrustedText  # noqa: PLC0415

        d = dict(src_dict)
        evidence_refs = []
        _evidence_refs = d.pop("evidence_refs")
        for evidence_refs_item_data in _evidence_refs:
            evidence_refs_item = CustomerEvidenceRef.from_dict(evidence_refs_item_data)

            evidence_refs.append(evidence_refs_item)

        def _parse_explanation(data: object) -> None | Unset | UntrustedText:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                explanation_type_0 = UntrustedText.from_dict(data)

                return explanation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UntrustedText, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        finding_support = cls(
            evidence_refs=evidence_refs,
            explanation=explanation,
        )

        finding_support.additional_properties = d
        return finding_support

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
