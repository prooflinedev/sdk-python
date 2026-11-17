from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RunProgress")


@_attrs_define
class RunProgress:
    """Where an unfinished review's runs stand.

    Attributes:
        attempts (int): Attempts begun by the run in `state`, counting worker claims.
        state (Literal['QUEUED'] | Literal['RETRY_SCHEDULED'] | Literal['RUNNING'] | Literal['WAITING']): What an
            unfinished review's runs are doing now.
        due_at (datetime.datetime | None | Unset): When the run in `state` is due: in the past for `QUEUED`, the next
             attempt for `RETRY_SCHEDULED` and the next check for `WAITING`. Null
             for `RUNNING`.
        last_progress_at (datetime.datetime | None | Unset): When any of the review's runs last recorded a completed
            step. Null
             before the first.
    """

    attempts: int
    state: Literal["QUEUED"] | Literal["RETRY_SCHEDULED"] | Literal["RUNNING"] | Literal["WAITING"]
    due_at: datetime.datetime | None | Unset = UNSET
    last_progress_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attempts = self.attempts

        state: (
            Literal["QUEUED"] | Literal["RETRY_SCHEDULED"] | Literal["RUNNING"] | Literal["WAITING"]
        )
        state = self.state

        due_at: None | str | Unset
        if isinstance(self.due_at, Unset):
            due_at = UNSET
        elif isinstance(self.due_at, datetime.datetime):
            due_at = self.due_at.isoformat()
        else:
            due_at = self.due_at

        last_progress_at: None | str | Unset
        if isinstance(self.last_progress_at, Unset):
            last_progress_at = UNSET
        elif isinstance(self.last_progress_at, datetime.datetime):
            last_progress_at = self.last_progress_at.isoformat()
        else:
            last_progress_at = self.last_progress_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attempts": attempts,
                "state": state,
            }
        )
        if due_at is not UNSET:
            field_dict["due_at"] = due_at
        if last_progress_at is not UNSET:
            field_dict["last_progress_at"] = last_progress_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attempts = d.pop("attempts")

        def _parse_state(
            data: object,
        ) -> (
            Literal["QUEUED"] | Literal["RETRY_SCHEDULED"] | Literal["RUNNING"] | Literal["WAITING"]
        ):
            try:
                if not (type(data) is str and data == "WAITING"):
                    raise TypeError()
                componentsschemas_run_progress_state_type_0 = cast(Literal["WAITING"], data)
                if componentsschemas_run_progress_state_type_0 != "WAITING":
                    raise ValueError(
                        f"/components/schemas/RunProgressState_type_0 must match const 'WAITING', got '{componentsschemas_run_progress_state_type_0}'"
                    )
                return componentsschemas_run_progress_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "QUEUED"):
                    raise TypeError()
                componentsschemas_run_progress_state_type_1 = cast(Literal["QUEUED"], data)
                if componentsschemas_run_progress_state_type_1 != "QUEUED":
                    raise ValueError(
                        f"/components/schemas/RunProgressState_type_1 must match const 'QUEUED', got '{componentsschemas_run_progress_state_type_1}'"
                    )
                return componentsschemas_run_progress_state_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "RUNNING"):
                    raise TypeError()
                componentsschemas_run_progress_state_type_2 = cast(Literal["RUNNING"], data)
                if componentsschemas_run_progress_state_type_2 != "RUNNING":
                    raise ValueError(
                        f"/components/schemas/RunProgressState_type_2 must match const 'RUNNING', got '{componentsschemas_run_progress_state_type_2}'"
                    )
                return componentsschemas_run_progress_state_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "RETRY_SCHEDULED"):
                raise TypeError()
            componentsschemas_run_progress_state_type_3 = cast(Literal["RETRY_SCHEDULED"], data)
            if componentsschemas_run_progress_state_type_3 != "RETRY_SCHEDULED":
                raise ValueError(
                    f"/components/schemas/RunProgressState_type_3 must match const 'RETRY_SCHEDULED', got '{componentsschemas_run_progress_state_type_3}'"
                )
            return componentsschemas_run_progress_state_type_3

        state = _parse_state(d.pop("state"))

        def _parse_due_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                due_at_type_0 = datetime.datetime.fromisoformat(data)

                return due_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        due_at = _parse_due_at(d.pop("due_at", UNSET))

        def _parse_last_progress_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_progress_at_type_0 = datetime.datetime.fromisoformat(data)

                return last_progress_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_progress_at = _parse_last_progress_at(d.pop("last_progress_at", UNSET))

        run_progress = cls(
            attempts=attempts,
            state=state,
            due_at=due_at,
            last_progress_at=last_progress_at,
        )

        run_progress.additional_properties = d
        return run_progress

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
