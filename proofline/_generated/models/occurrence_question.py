from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OccurrenceQuestion")


@_attrs_define
class OccurrenceQuestion:
    """One deferred question as the gate presents it.

    Attributes:
        assessment_id (UUID):
        family_key (str):
        family_version (int):
        state (Literal['NOT_EXECUTED'] | Literal['PENDING'] | Literal['RECORDED'] | Literal['UNBOUND']): Where one
            deferred question stands.
        code (None | str | Unset): World's binding or refusal code, or the control plane's own gap.
        observed_result (None | str | Unset): World's observed result once it recorded the question.
        outcome_id (None | str | Unset):
    """

    assessment_id: UUID
    family_key: str
    family_version: int
    state: Literal["NOT_EXECUTED"] | Literal["PENDING"] | Literal["RECORDED"] | Literal["UNBOUND"]
    code: None | str | Unset = UNSET
    observed_result: None | str | Unset = UNSET
    outcome_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_id = str(self.assessment_id)

        family_key = self.family_key

        family_version = self.family_version

        state: (
            Literal["NOT_EXECUTED"] | Literal["PENDING"] | Literal["RECORDED"] | Literal["UNBOUND"]
        )
        state = self.state

        code: None | str | Unset
        if isinstance(self.code, Unset):
            code = UNSET
        else:
            code = self.code

        observed_result: None | str | Unset
        if isinstance(self.observed_result, Unset):
            observed_result = UNSET
        else:
            observed_result = self.observed_result

        outcome_id: None | str | Unset
        if isinstance(self.outcome_id, Unset):
            outcome_id = UNSET
        else:
            outcome_id = self.outcome_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_id": assessment_id,
                "family_key": family_key,
                "family_version": family_version,
                "state": state,
            }
        )
        if code is not UNSET:
            field_dict["code"] = code
        if observed_result is not UNSET:
            field_dict["observed_result"] = observed_result
        if outcome_id is not UNSET:
            field_dict["outcome_id"] = outcome_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assessment_id = UUID(d.pop("assessment_id"))

        family_key = d.pop("family_key")

        family_version = d.pop("family_version")

        def _parse_state(
            data: object,
        ) -> (
            Literal["NOT_EXECUTED"] | Literal["PENDING"] | Literal["RECORDED"] | Literal["UNBOUND"]
        ):
            try:
                if not (type(data) is str and data == "PENDING"):
                    raise TypeError()
                componentsschemas_question_state_type_0 = cast(Literal["PENDING"], data)
                if componentsschemas_question_state_type_0 != "PENDING":
                    raise ValueError(
                        f"/components/schemas/QuestionState_type_0 must match const 'PENDING', got '{componentsschemas_question_state_type_0}'"
                    )
                return componentsschemas_question_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "RECORDED"):
                    raise TypeError()
                componentsschemas_question_state_type_1 = cast(Literal["RECORDED"], data)
                if componentsschemas_question_state_type_1 != "RECORDED":
                    raise ValueError(
                        f"/components/schemas/QuestionState_type_1 must match const 'RECORDED', got '{componentsschemas_question_state_type_1}'"
                    )
                return componentsschemas_question_state_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNBOUND"):
                    raise TypeError()
                componentsschemas_question_state_type_2 = cast(Literal["UNBOUND"], data)
                if componentsschemas_question_state_type_2 != "UNBOUND":
                    raise ValueError(
                        f"/components/schemas/QuestionState_type_2 must match const 'UNBOUND', got '{componentsschemas_question_state_type_2}'"
                    )
                return componentsschemas_question_state_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "NOT_EXECUTED"):
                raise TypeError()
            componentsschemas_question_state_type_3 = cast(Literal["NOT_EXECUTED"], data)
            if componentsschemas_question_state_type_3 != "NOT_EXECUTED":
                raise ValueError(
                    f"/components/schemas/QuestionState_type_3 must match const 'NOT_EXECUTED', got '{componentsschemas_question_state_type_3}'"
                )
            return componentsschemas_question_state_type_3

        state = _parse_state(d.pop("state"))

        def _parse_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        code = _parse_code(d.pop("code", UNSET))

        def _parse_observed_result(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        observed_result = _parse_observed_result(d.pop("observed_result", UNSET))

        def _parse_outcome_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        outcome_id = _parse_outcome_id(d.pop("outcome_id", UNSET))

        occurrence_question = cls(
            assessment_id=assessment_id,
            family_key=family_key,
            family_version=family_version,
            state=state,
            code=code,
            observed_result=observed_result,
            outcome_id=outcome_id,
        )

        occurrence_question.additional_properties = d
        return occurrence_question

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
