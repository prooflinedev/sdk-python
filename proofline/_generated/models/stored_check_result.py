from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.stored_check_outcome import StoredCheckOutcome
from ..models.stored_check_result_source import StoredCheckResultSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="StoredCheckResult")


@_attrs_define
class StoredCheckResult:
    """The newest result of a stored check: its newest settled rerun at a later
    pull request head, or the reproduction's own head run when it has not
    run again.

       Attributes:
           result (StoredCheckOutcome): What the test did: `FAILED` as at the reproduction or otherwise,
                `DID_NOT_FAIL` when it exited cleanly, which shows only that this test
                did not fail under the conditions it exercised, or `UNAVAILABLE` when it
                could not answer.
           source (StoredCheckResultSource):
           commit_sha (None | str | Unset): The commit the check ran at, or would have run at when a rerun could
                not start.
           reason (None | str | Unset): Why a rerun did not pass, such as `STILL_FAILS` or
                `SERVICE_NOT_STARTED`. Absent for a pass and for the reproduction.
    """

    result: StoredCheckOutcome
    source: StoredCheckResultSource
    commit_sha: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = self.result.value

        source = self.source.value

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "result": result,
                "source": source,
            }
        )
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        result = StoredCheckOutcome(d.pop("result"))

        source = StoredCheckResultSource(d.pop("source"))

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        stored_check_result = cls(
            result=result,
            source=source,
            commit_sha=commit_sha,
            reason=reason,
        )

        stored_check_result.additional_properties = d
        return stored_check_result

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
