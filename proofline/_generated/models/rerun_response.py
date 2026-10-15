from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RerunResponse")


@_attrs_define
class RerunResponse:
    """Manual rerun: a new review of the same immutable subjects, under a fresh
    trigger key so history accumulates instead of overwriting.

       Attributes:
           public_key (str): The new review's stable public address.
           review_id (UUID): The new review's identifier.
           pull_request_number (int | None | Unset): The pull request number. Absent for a deployment review.
           repository_name (None | str | Unset): The repository's name within its owner. Absent when the original review
               names no repository.
           run_number (int | None | Unset): The new review's one-based ordinal within its pull request. Absent for a
               deployment review.
    """

    public_key: str
    review_id: UUID
    pull_request_number: int | None | Unset = UNSET
    repository_name: None | str | Unset = UNSET
    run_number: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        public_key = self.public_key

        review_id = str(self.review_id)

        pull_request_number: int | None | Unset
        if isinstance(self.pull_request_number, Unset):
            pull_request_number = UNSET
        else:
            pull_request_number = self.pull_request_number

        repository_name: None | str | Unset
        if isinstance(self.repository_name, Unset):
            repository_name = UNSET
        else:
            repository_name = self.repository_name

        run_number: int | None | Unset
        if isinstance(self.run_number, Unset):
            run_number = UNSET
        else:
            run_number = self.run_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "public_key": public_key,
                "review_id": review_id,
            }
        )
        if pull_request_number is not UNSET:
            field_dict["pull_request_number"] = pull_request_number
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name
        if run_number is not UNSET:
            field_dict["run_number"] = run_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        public_key = d.pop("public_key")

        review_id = UUID(d.pop("review_id"))

        def _parse_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_number = _parse_pull_request_number(d.pop("pull_request_number", UNSET))

        def _parse_repository_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_name = _parse_repository_name(d.pop("repository_name", UNSET))

        def _parse_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        run_number = _parse_run_number(d.pop("run_number", UNSET))

        rerun_response = cls(
            public_key=public_key,
            review_id=review_id,
            pull_request_number=pull_request_number,
            repository_name=repository_name,
            run_number=run_number,
        )

        rerun_response.additional_properties = d
        return rerun_response

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
