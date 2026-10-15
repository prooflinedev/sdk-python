from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FindingPlacementView")


@_attrs_define
class FindingPlacementView:
    """
    Attributes:
        placement (Literal['CHECK_ONLY'] | Literal['INLINE'] | Literal['WITHHELD']): Where the comment gate placed a
            finding. The placement is what the gate
             decided, not proof that a comment was posted.
        reason (str): Why the finding has this placement, in Proofline's own words.
    """

    placement: Literal["CHECK_ONLY"] | Literal["INLINE"] | Literal["WITHHELD"]
    reason: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        placement: Literal["CHECK_ONLY"] | Literal["INLINE"] | Literal["WITHHELD"]
        placement = self.placement

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "placement": placement,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_placement(
            data: object,
        ) -> Literal["CHECK_ONLY"] | Literal["INLINE"] | Literal["WITHHELD"]:
            try:
                if not (type(data) is str and data == "INLINE"):
                    raise TypeError()
                componentsschemas_finding_placement_type_0 = cast(Literal["INLINE"], data)
                if componentsschemas_finding_placement_type_0 != "INLINE":
                    raise ValueError(
                        f"/components/schemas/FindingPlacement_type_0 must match const 'INLINE', got '{componentsschemas_finding_placement_type_0}'"
                    )
                return componentsschemas_finding_placement_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "CHECK_ONLY"):
                    raise TypeError()
                componentsschemas_finding_placement_type_1 = cast(Literal["CHECK_ONLY"], data)
                if componentsschemas_finding_placement_type_1 != "CHECK_ONLY":
                    raise ValueError(
                        f"/components/schemas/FindingPlacement_type_1 must match const 'CHECK_ONLY', got '{componentsschemas_finding_placement_type_1}'"
                    )
                return componentsschemas_finding_placement_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "WITHHELD"):
                raise TypeError()
            componentsschemas_finding_placement_type_2 = cast(Literal["WITHHELD"], data)
            if componentsschemas_finding_placement_type_2 != "WITHHELD":
                raise ValueError(
                    f"/components/schemas/FindingPlacement_type_2 must match const 'WITHHELD', got '{componentsschemas_finding_placement_type_2}'"
                )
            return componentsschemas_finding_placement_type_2

        placement = _parse_placement(d.pop("placement"))

        reason = d.pop("reason")

        finding_placement_view = cls(
            placement=placement,
            reason=reason,
        )

        finding_placement_view.additional_properties = d
        return finding_placement_view

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
