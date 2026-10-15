from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ChangeCountView")


@_attrs_define
class ChangeCountView:
    """How many conditions are of one change at one revision.

    Attributes:
        change (Literal['CHANGED'] | Literal['INTRODUCED'] | Literal['RESOLVED'] | Literal['UNATTRIBUTED'] |
            Literal['UNCHANGED']): How one condition relates to the review's base revision.
        count (int): How many conditions have this `change` at this `revision`, over every
             condition, listed or not.
        revision (Literal['BASE_CODE_REVISION'] | Literal['PROPOSED_CODE_REVISION']):
    """

    change: (
        Literal["CHANGED"]
        | Literal["INTRODUCED"]
        | Literal["RESOLVED"]
        | Literal["UNATTRIBUTED"]
        | Literal["UNCHANGED"]
    )
    count: int
    revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        change: (
            Literal["CHANGED"]
            | Literal["INTRODUCED"]
            | Literal["RESOLVED"]
            | Literal["UNATTRIBUTED"]
            | Literal["UNCHANGED"]
        )
        change = self.change

        count = self.count

        revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "change": change,
                "count": count,
                "revision": revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_change(
            data: object,
        ) -> (
            Literal["CHANGED"]
            | Literal["INTRODUCED"]
            | Literal["RESOLVED"]
            | Literal["UNATTRIBUTED"]
            | Literal["UNCHANGED"]
        ):
            try:
                if not (type(data) is str and data == "INTRODUCED"):
                    raise TypeError()
                componentsschemas_attributed_change_type_0 = cast(Literal["INTRODUCED"], data)
                if componentsschemas_attributed_change_type_0 != "INTRODUCED":
                    raise ValueError(
                        f"/components/schemas/AttributedChange_type_0 must match const 'INTRODUCED', got '{componentsschemas_attributed_change_type_0}'"
                    )
                return componentsschemas_attributed_change_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "CHANGED"):
                    raise TypeError()
                componentsschemas_attributed_change_type_1 = cast(Literal["CHANGED"], data)
                if componentsschemas_attributed_change_type_1 != "CHANGED":
                    raise ValueError(
                        f"/components/schemas/AttributedChange_type_1 must match const 'CHANGED', got '{componentsschemas_attributed_change_type_1}'"
                    )
                return componentsschemas_attributed_change_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNCHANGED"):
                    raise TypeError()
                componentsschemas_attributed_change_type_2 = cast(Literal["UNCHANGED"], data)
                if componentsschemas_attributed_change_type_2 != "UNCHANGED":
                    raise ValueError(
                        f"/components/schemas/AttributedChange_type_2 must match const 'UNCHANGED', got '{componentsschemas_attributed_change_type_2}'"
                    )
                return componentsschemas_attributed_change_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "RESOLVED"):
                    raise TypeError()
                componentsschemas_attributed_change_type_3 = cast(Literal["RESOLVED"], data)
                if componentsschemas_attributed_change_type_3 != "RESOLVED":
                    raise ValueError(
                        f"/components/schemas/AttributedChange_type_3 must match const 'RESOLVED', got '{componentsschemas_attributed_change_type_3}'"
                    )
                return componentsschemas_attributed_change_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "UNATTRIBUTED"):
                raise TypeError()
            componentsschemas_attributed_change_type_4 = cast(Literal["UNATTRIBUTED"], data)
            if componentsschemas_attributed_change_type_4 != "UNATTRIBUTED":
                raise ValueError(
                    f"/components/schemas/AttributedChange_type_4 must match const 'UNATTRIBUTED', got '{componentsschemas_attributed_change_type_4}'"
                )
            return componentsschemas_attributed_change_type_4

        change = _parse_change(d.pop("change"))

        count = d.pop("count")

        def _parse_revision(
            data: object,
        ) -> Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]:
            try:
                if not (type(data) is str and data == "PROPOSED_CODE_REVISION"):
                    raise TypeError()
                componentsschemas_attributed_revision_type_0 = cast(
                    Literal["PROPOSED_CODE_REVISION"], data
                )
                if componentsschemas_attributed_revision_type_0 != "PROPOSED_CODE_REVISION":
                    raise ValueError(
                        f"/components/schemas/AttributedRevision_type_0 must match const 'PROPOSED_CODE_REVISION', got '{componentsschemas_attributed_revision_type_0}'"
                    )
                return componentsschemas_attributed_revision_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "BASE_CODE_REVISION"):
                raise TypeError()
            componentsschemas_attributed_revision_type_1 = cast(Literal["BASE_CODE_REVISION"], data)
            if componentsschemas_attributed_revision_type_1 != "BASE_CODE_REVISION":
                raise ValueError(
                    f"/components/schemas/AttributedRevision_type_1 must match const 'BASE_CODE_REVISION', got '{componentsschemas_attributed_revision_type_1}'"
                )
            return componentsschemas_attributed_revision_type_1

        revision = _parse_revision(d.pop("revision"))

        change_count_view = cls(
            change=change,
            count=count,
            revision=revision,
        )

        change_count_view.additional_properties = d
        return change_count_view

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
