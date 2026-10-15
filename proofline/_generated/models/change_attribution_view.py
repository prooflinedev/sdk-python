from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attributed_condition_view import AttributedConditionView
    from ..models.change_count_view import ChangeCountView
    from ..models.complete_record_view import CompleteRecordView


T = TypeVar("T", bound="ChangeAttributionView")


@_attrs_define
class ChangeAttributionView:
    """Which conditions behind a check's result the change brought, and which
    World found at the review's base revision. It sits beside the result and
    never changes it: a condition already at the base is still a condition.

       Attributes:
           condition_count (int): How many conditions World attributed, listed or not. Zero unless
                `status` is `COMPARED`.
           conditions (list[AttributedConditionView]): Every condition, each once, in World's order, never netted against
                another. Empty unless `status` is `COMPARED`, and empty when some are
                omitted: it never lists only some of them.
           counts (list[ChangeCountView]): How many conditions there are of each change at each revision, over
                every condition, listed or not. Changes with none are left out.
           omitted_condition_count (int): How many of those conditions this response does not list. Zero when
                the result kept World's attribution whole. Otherwise the result kept a
                summary: `listed_conditions` lists the first ones, `counts` is still
                exact, and World's recorded evaluation holds every condition.
           status (Literal['COMPARED'] | Literal['UNAVAILABLE'] | Literal['UNREADABLE']):
           complete_record (CompleteRecordView | None | Unset): Where every condition is recorded when some are omitted.
               Absent when
                `conditions` lists them all.
           detail_code (None | str | Unset): World's code for why it could not read that revision, such as
                `BASE_REVIEWED_TREE_NOT_DECLARED`. Present exactly when `status` is
                `UNAVAILABLE`.
           listed_conditions (list[AttributedConditionView] | None | Unset): The conditions a summary lists when some are
               omitted: the first ones
                in the order `counts` gives, each whole, at most 50 and always fewer
                than `condition_count`. Present exactly when `omitted_condition_count`
                is not zero.
           revision (Literal['BASE_CODE_REVISION'] | Literal['PROPOSED_CODE_REVISION'] | None | Unset): The revision World
               could not read. Present exactly when `status` is
                `UNAVAILABLE`.
    """

    condition_count: int
    conditions: list[AttributedConditionView]
    counts: list[ChangeCountView]
    omitted_condition_count: int
    status: Literal["COMPARED"] | Literal["UNAVAILABLE"] | Literal["UNREADABLE"]
    complete_record: CompleteRecordView | None | Unset = UNSET
    detail_code: None | str | Unset = UNSET
    listed_conditions: list[AttributedConditionView] | None | Unset = UNSET
    revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"] | None | Unset = (
        UNSET
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.complete_record_view import CompleteRecordView  # noqa: PLC0415

        condition_count = self.condition_count

        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        counts = []
        for counts_item_data in self.counts:
            counts_item = counts_item_data.to_dict()
            counts.append(counts_item)

        omitted_condition_count = self.omitted_condition_count

        status: Literal["COMPARED"] | Literal["UNAVAILABLE"] | Literal["UNREADABLE"]
        status = self.status

        complete_record: dict[str, Any] | None | Unset
        if isinstance(self.complete_record, Unset):
            complete_record = UNSET
        elif isinstance(self.complete_record, CompleteRecordView):
            complete_record = self.complete_record.to_dict()
        else:
            complete_record = self.complete_record

        detail_code: None | str | Unset
        if isinstance(self.detail_code, Unset):
            detail_code = UNSET
        else:
            detail_code = self.detail_code

        listed_conditions: list[dict[str, Any]] | None | Unset
        if isinstance(self.listed_conditions, Unset):
            listed_conditions = UNSET
        elif isinstance(self.listed_conditions, list):
            listed_conditions = []
            for listed_conditions_type_0_item_data in self.listed_conditions:
                listed_conditions_type_0_item = listed_conditions_type_0_item_data.to_dict()
                listed_conditions.append(listed_conditions_type_0_item)

        else:
            listed_conditions = self.listed_conditions

        revision: Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"] | None | Unset
        if isinstance(self.revision, Unset):
            revision = UNSET
        else:
            revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "condition_count": condition_count,
                "conditions": conditions,
                "counts": counts,
                "omitted_condition_count": omitted_condition_count,
                "status": status,
            }
        )
        if complete_record is not UNSET:
            field_dict["complete_record"] = complete_record
        if detail_code is not UNSET:
            field_dict["detail_code"] = detail_code
        if listed_conditions is not UNSET:
            field_dict["listed_conditions"] = listed_conditions
        if revision is not UNSET:
            field_dict["revision"] = revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attributed_condition_view import AttributedConditionView  # noqa: PLC0415
        from ..models.change_count_view import ChangeCountView  # noqa: PLC0415
        from ..models.complete_record_view import CompleteRecordView  # noqa: PLC0415

        d = dict(src_dict)
        condition_count = d.pop("condition_count")

        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = AttributedConditionView.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        counts = []
        _counts = d.pop("counts")
        for counts_item_data in _counts:
            counts_item = ChangeCountView.from_dict(counts_item_data)

            counts.append(counts_item)

        omitted_condition_count = d.pop("omitted_condition_count")

        def _parse_status(
            data: object,
        ) -> Literal["COMPARED"] | Literal["UNAVAILABLE"] | Literal["UNREADABLE"]:
            try:
                if not (type(data) is str and data == "COMPARED"):
                    raise TypeError()
                componentsschemas_attribution_status_type_0 = cast(Literal["COMPARED"], data)
                if componentsschemas_attribution_status_type_0 != "COMPARED":
                    raise ValueError(
                        f"/components/schemas/AttributionStatus_type_0 must match const 'COMPARED', got '{componentsschemas_attribution_status_type_0}'"
                    )
                return componentsschemas_attribution_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNAVAILABLE"):
                    raise TypeError()
                componentsschemas_attribution_status_type_1 = cast(Literal["UNAVAILABLE"], data)
                if componentsschemas_attribution_status_type_1 != "UNAVAILABLE":
                    raise ValueError(
                        f"/components/schemas/AttributionStatus_type_1 must match const 'UNAVAILABLE', got '{componentsschemas_attribution_status_type_1}'"
                    )
                return componentsschemas_attribution_status_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "UNREADABLE"):
                raise TypeError()
            componentsschemas_attribution_status_type_2 = cast(Literal["UNREADABLE"], data)
            if componentsschemas_attribution_status_type_2 != "UNREADABLE":
                raise ValueError(
                    f"/components/schemas/AttributionStatus_type_2 must match const 'UNREADABLE', got '{componentsschemas_attribution_status_type_2}'"
                )
            return componentsschemas_attribution_status_type_2

        status = _parse_status(d.pop("status"))

        def _parse_complete_record(data: object) -> CompleteRecordView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                complete_record_type_0 = CompleteRecordView.from_dict(data)

                return complete_record_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CompleteRecordView | None | Unset, data)

        complete_record = _parse_complete_record(d.pop("complete_record", UNSET))

        def _parse_detail_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail_code = _parse_detail_code(d.pop("detail_code", UNSET))

        def _parse_listed_conditions(data: object) -> list[AttributedConditionView] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                listed_conditions_type_0 = []
                _listed_conditions_type_0 = data
                for listed_conditions_type_0_item_data in _listed_conditions_type_0:
                    listed_conditions_type_0_item = AttributedConditionView.from_dict(
                        listed_conditions_type_0_item_data
                    )

                    listed_conditions_type_0.append(listed_conditions_type_0_item)

                return listed_conditions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AttributedConditionView] | None | Unset, data)

        listed_conditions = _parse_listed_conditions(d.pop("listed_conditions", UNSET))

        def _parse_revision(
            data: object,
        ) -> Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
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
            try:
                if not (type(data) is str and data == "BASE_CODE_REVISION"):
                    raise TypeError()
                componentsschemas_attributed_revision_type_1 = cast(
                    Literal["BASE_CODE_REVISION"], data
                )
                if componentsschemas_attributed_revision_type_1 != "BASE_CODE_REVISION":
                    raise ValueError(
                        f"/components/schemas/AttributedRevision_type_1 must match const 'BASE_CODE_REVISION', got '{componentsschemas_attributed_revision_type_1}'"
                    )
                return componentsschemas_attributed_revision_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["BASE_CODE_REVISION"] | Literal["PROPOSED_CODE_REVISION"] | None | Unset,
                data,
            )

        revision = _parse_revision(d.pop("revision", UNSET))

        change_attribution_view = cls(
            condition_count=condition_count,
            conditions=conditions,
            counts=counts,
            omitted_condition_count=omitted_condition_count,
            status=status,
            complete_record=complete_record,
            detail_code=detail_code,
            listed_conditions=listed_conditions,
            revision=revision,
        )

        change_attribution_view.additional_properties = d
        return change_attribution_view

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
