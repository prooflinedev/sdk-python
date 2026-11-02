from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScanRequestBody")


@_attrs_define
class ScanRequestBody:
    """One request to scan a ref or an exact commit of the repository.

    Attributes:
        budget_credits (int): The credits the whole scan may spend, at most the organization's
             on-demand ceiling.
        request_id (UUID): The caller's identity for this request. Sending it again returns the
             first resolution instead of scanning again.
        commit_sha (None | str | Unset): An exact commit. Name it or `ref`.
        ref (None | str | Unset): A ref, resolved once when the request arrives. Name it or `commit_sha`.
    """

    budget_credits: int
    request_id: UUID
    commit_sha: None | str | Unset = UNSET
    ref: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        budget_credits = self.budget_credits

        request_id = str(self.request_id)

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        ref: None | str | Unset
        if isinstance(self.ref, Unset):
            ref = UNSET
        else:
            ref = self.ref

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "budget_credits": budget_credits,
                "request_id": request_id,
            }
        )
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if ref is not UNSET:
            field_dict["ref"] = ref

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        budget_credits = d.pop("budget_credits")

        request_id = UUID(d.pop("request_id"))

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ref = _parse_ref(d.pop("ref", UNSET))

        scan_request_body = cls(
            budget_credits=budget_credits,
            request_id=request_id,
            commit_sha=commit_sha,
            ref=ref,
        )

        return scan_request_body
