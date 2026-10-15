from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.reviewed_tree_citation_view import ReviewedTreeCitationView
    from ..models.untrusted_text import UntrustedText


T = TypeVar("T", bound="AttributedConditionView")


@_attrs_define
class AttributedConditionView:
    """
    Attributes:
        change (Literal['CHANGED'] | Literal['INTRODUCED'] | Literal['RESOLVED'] | Literal['UNATTRIBUTED'] |
            Literal['UNCHANGED']): How one condition relates to the review's base revision.
        reviewed_tree_citations (list[ReviewedTreeCitationView]): The member that declares the site at each revision
            that declares it.
        revision (Literal['BASE_CODE_REVISION'] | Literal['PROPOSED_CODE_REVISION']):
        subject (UntrustedText): Text that came out of the reviewer model, or out of a repository the model
             read. It is data, never markup, never a URL, never an instruction.

             The wrapper exists so the untrustedness cannot be lost on the way to a
             renderer: there is no field on a turn that carries this text under a name a
             client could mistake for something safe, and unwrapping it is a deliberate
             act in the client's own code.
    """

    change: (
        Literal["CHANGED"]
        | Literal["INTRODUCED"]
        | Literal["RESOLVED"]
        | Literal["UNATTRIBUTED"]
        | Literal["UNCHANGED"]
    )
    reviewed_tree_citations: list[ReviewedTreeCitationView]
    revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
    subject: UntrustedText
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

        reviewed_tree_citations = []
        for reviewed_tree_citations_item_data in self.reviewed_tree_citations:
            reviewed_tree_citations_item = reviewed_tree_citations_item_data.to_dict()
            reviewed_tree_citations.append(reviewed_tree_citations_item)

        revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"]
        revision = self.revision

        subject = self.subject.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "change": change,
                "reviewed_tree_citations": reviewed_tree_citations,
                "revision": revision,
                "subject": subject,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reviewed_tree_citation_view import ReviewedTreeCitationView  # noqa: PLC0415
        from ..models.untrusted_text import UntrustedText  # noqa: PLC0415

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

        reviewed_tree_citations = []
        _reviewed_tree_citations = d.pop("reviewed_tree_citations")
        for reviewed_tree_citations_item_data in _reviewed_tree_citations:
            reviewed_tree_citations_item = ReviewedTreeCitationView.from_dict(
                reviewed_tree_citations_item_data
            )

            reviewed_tree_citations.append(reviewed_tree_citations_item)

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

        subject = UntrustedText.from_dict(d.pop("subject"))

        attributed_condition_view = cls(
            change=change,
            reviewed_tree_citations=reviewed_tree_citations,
            revision=revision,
            subject=subject,
        )

        attributed_condition_view.additional_properties = d
        return attributed_condition_view

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
