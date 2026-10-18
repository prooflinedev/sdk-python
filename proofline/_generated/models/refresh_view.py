from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RefreshView")


@_attrs_define
class RefreshView:
    """A recorded refresh decision, as the console shows it.

    Attributes:
        mode (str): `INCREMENTAL` reviews only the files the push touched and carries the
             earlier review's untouched findings forward; `FULL` reviews the whole change.
        decided_by (None | str | Unset): What decided: `FLOOR`, a refresh rule that always reviews the whole
             change; `JEV`, Proofline's decision model within those rules; or
             `FALLBACK`, the refresh rules because the model did not decide.
             Absent for a full review a person requested, and for reviews decided
             before it was recorded.
        reason (None | str | Unset): Why, in words. Server text that may name repository paths.
        refreshes_review_id (None | Unset | UUID): The review this one refreshes. Absent for a full review a person
            requested.
    """

    mode: str
    decided_by: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    refreshes_review_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode

        decided_by: None | str | Unset
        if isinstance(self.decided_by, Unset):
            decided_by = UNSET
        else:
            decided_by = self.decided_by

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        refreshes_review_id: None | str | Unset
        if isinstance(self.refreshes_review_id, Unset):
            refreshes_review_id = UNSET
        elif isinstance(self.refreshes_review_id, UUID):
            refreshes_review_id = str(self.refreshes_review_id)
        else:
            refreshes_review_id = self.refreshes_review_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mode": mode,
            }
        )
        if decided_by is not UNSET:
            field_dict["decided_by"] = decided_by
        if reason is not UNSET:
            field_dict["reason"] = reason
        if refreshes_review_id is not UNSET:
            field_dict["refreshes_review_id"] = refreshes_review_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mode = d.pop("mode")

        def _parse_decided_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decided_by = _parse_decided_by(d.pop("decided_by", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_refreshes_review_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                refreshes_review_id_type_0 = UUID(data)

                return refreshes_review_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        refreshes_review_id = _parse_refreshes_review_id(d.pop("refreshes_review_id", UNSET))

        refresh_view = cls(
            mode=mode,
            decided_by=decided_by,
            reason=reason,
            refreshes_review_id=refreshes_review_id,
        )

        refresh_view.additional_properties = d
        return refresh_view

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
