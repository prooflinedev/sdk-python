from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.approval_gap import ApprovalGap
    from ..models.occurrence_question import OccurrenceQuestion


T = TypeVar("T", bound="OccurrenceCapture")


@_attrs_define
class OccurrenceCapture:
    """The capture of one observed execution of a gate's deployment.

    Attributes:
        approval_gaps (list[ApprovalGap]): Assessments whose approval could defer nothing, with the reason.
        questions (list[OccurrenceQuestion]): Deferred questions and their binding or observed results for this
            occurrence.
        state (Literal['INCOMPLETE'] | Literal['NOT_EXECUTED'] | Literal['PENDING'] | Literal['RECORDED'] |
            Literal['UNBOUND']): How the capture ended.
        detail (None | str | Unset): Explanation of the capture's outcome, when available.
        occurrence_key (None | str | Unset): Retained identity of the deployment occurrence, when available.
    """

    approval_gaps: list[ApprovalGap]
    questions: list[OccurrenceQuestion]
    state: (
        Literal["INCOMPLETE"]
        | Literal["NOT_EXECUTED"]
        | Literal["PENDING"]
        | Literal["RECORDED"]
        | Literal["UNBOUND"]
    )
    detail: None | str | Unset = UNSET
    occurrence_key: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        approval_gaps = []
        for approval_gaps_item_data in self.approval_gaps:
            approval_gaps_item = approval_gaps_item_data.to_dict()
            approval_gaps.append(approval_gaps_item)

        questions = []
        for questions_item_data in self.questions:
            questions_item = questions_item_data.to_dict()
            questions.append(questions_item)

        state: (
            Literal["INCOMPLETE"]
            | Literal["NOT_EXECUTED"]
            | Literal["PENDING"]
            | Literal["RECORDED"]
            | Literal["UNBOUND"]
        )
        state = self.state

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        occurrence_key: None | str | Unset
        if isinstance(self.occurrence_key, Unset):
            occurrence_key = UNSET
        else:
            occurrence_key = self.occurrence_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "approval_gaps": approval_gaps,
                "questions": questions,
                "state": state,
            }
        )
        if detail is not UNSET:
            field_dict["detail"] = detail
        if occurrence_key is not UNSET:
            field_dict["occurrence_key"] = occurrence_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.approval_gap import ApprovalGap  # noqa: PLC0415
        from ..models.occurrence_question import OccurrenceQuestion  # noqa: PLC0415

        d = dict(src_dict)
        approval_gaps = []
        _approval_gaps = d.pop("approval_gaps")
        for approval_gaps_item_data in _approval_gaps:
            approval_gaps_item = ApprovalGap.from_dict(approval_gaps_item_data)

            approval_gaps.append(approval_gaps_item)

        questions = []
        _questions = d.pop("questions")
        for questions_item_data in _questions:
            questions_item = OccurrenceQuestion.from_dict(questions_item_data)

            questions.append(questions_item)

        def _parse_state(
            data: object,
        ) -> (
            Literal["INCOMPLETE"]
            | Literal["NOT_EXECUTED"]
            | Literal["PENDING"]
            | Literal["RECORDED"]
            | Literal["UNBOUND"]
        ):
            try:
                if not (type(data) is str and data == "PENDING"):
                    raise TypeError()
                componentsschemas_capture_state_type_0 = cast(Literal["PENDING"], data)
                if componentsschemas_capture_state_type_0 != "PENDING":
                    raise ValueError(
                        f"/components/schemas/CaptureState_type_0 must match const 'PENDING', got '{componentsschemas_capture_state_type_0}'"
                    )
                return componentsschemas_capture_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "RECORDED"):
                    raise TypeError()
                componentsschemas_capture_state_type_1 = cast(Literal["RECORDED"], data)
                if componentsschemas_capture_state_type_1 != "RECORDED":
                    raise ValueError(
                        f"/components/schemas/CaptureState_type_1 must match const 'RECORDED', got '{componentsschemas_capture_state_type_1}'"
                    )
                return componentsschemas_capture_state_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNBOUND"):
                    raise TypeError()
                componentsschemas_capture_state_type_2 = cast(Literal["UNBOUND"], data)
                if componentsschemas_capture_state_type_2 != "UNBOUND":
                    raise ValueError(
                        f"/components/schemas/CaptureState_type_2 must match const 'UNBOUND', got '{componentsschemas_capture_state_type_2}'"
                    )
                return componentsschemas_capture_state_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NOT_EXECUTED"):
                    raise TypeError()
                componentsschemas_capture_state_type_3 = cast(Literal["NOT_EXECUTED"], data)
                if componentsschemas_capture_state_type_3 != "NOT_EXECUTED":
                    raise ValueError(
                        f"/components/schemas/CaptureState_type_3 must match const 'NOT_EXECUTED', got '{componentsschemas_capture_state_type_3}'"
                    )
                return componentsschemas_capture_state_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "INCOMPLETE"):
                raise TypeError()
            componentsschemas_capture_state_type_4 = cast(Literal["INCOMPLETE"], data)
            if componentsschemas_capture_state_type_4 != "INCOMPLETE":
                raise ValueError(
                    f"/components/schemas/CaptureState_type_4 must match const 'INCOMPLETE', got '{componentsschemas_capture_state_type_4}'"
                )
            return componentsschemas_capture_state_type_4

        state = _parse_state(d.pop("state"))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        def _parse_occurrence_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        occurrence_key = _parse_occurrence_key(d.pop("occurrence_key", UNSET))

        occurrence_capture = cls(
            approval_gaps=approval_gaps,
            questions=questions,
            state=state,
            detail=detail,
            occurrence_key=occurrence_key,
        )

        occurrence_capture.additional_properties = d
        return occurrence_capture

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
