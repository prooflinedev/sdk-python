from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define

from ..models.patch_trigger_source import PatchTriggerSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchReviewRequest")


@_attrs_define
class PatchReviewRequest:
    """Local changes to review: a unified diff against a commit GitHub has.

    Attributes:
        base_commit_sha (str): The full 40-character commit the patch applies to. GitHub must have
             it in this repository.
        patch (str): The changes as `git diff --no-ext-diff --no-color <base>` prints them,
             at most 5 MiB and 3000 files. Text changes only: binary changes,
             symbolic links and submodules are refused.
        trigger_source (None | PatchTriggerSource | Unset): The git hook that sent this request, when one did. A review
            recorded
             by an earlier identical request keeps the source it recorded.
        verify_finding_ids (list[UUID] | Unset): Open findings of one pull request in this repository to re-verify
             against the patch, at most 20. The review re-investigates each one
             and reports its outcome in `local_reverifications`; the pull
             request's findings are unchanged whatever it is. Requires an API
             token. Each finding's series takes at most 3 requests per patch, and
             the pull request at most 10 re-verification requests per hour,
             counted with those a coding agent makes through MCP.
    """

    base_commit_sha: str
    patch: str
    trigger_source: None | PatchTriggerSource | Unset = UNSET
    verify_finding_ids: list[UUID] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        base_commit_sha = self.base_commit_sha

        patch = self.patch

        trigger_source: None | str | Unset
        if isinstance(self.trigger_source, Unset):
            trigger_source = UNSET
        elif isinstance(self.trigger_source, PatchTriggerSource):
            trigger_source = self.trigger_source.value
        else:
            trigger_source = self.trigger_source

        verify_finding_ids: list[str] | Unset = UNSET
        if not isinstance(self.verify_finding_ids, Unset):
            verify_finding_ids = []
            for verify_finding_ids_item_data in self.verify_finding_ids:
                verify_finding_ids_item = str(verify_finding_ids_item_data)
                verify_finding_ids.append(verify_finding_ids_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "base_commit_sha": base_commit_sha,
                "patch": patch,
            }
        )
        if trigger_source is not UNSET:
            field_dict["trigger_source"] = trigger_source
        if verify_finding_ids is not UNSET:
            field_dict["verify_finding_ids"] = verify_finding_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_commit_sha = d.pop("base_commit_sha")

        patch = d.pop("patch")

        def _parse_trigger_source(data: object) -> None | PatchTriggerSource | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trigger_source_type_0 = PatchTriggerSource(data)

                return trigger_source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PatchTriggerSource | Unset, data)

        trigger_source = _parse_trigger_source(d.pop("trigger_source", UNSET))

        _verify_finding_ids = d.pop("verify_finding_ids", UNSET)
        verify_finding_ids: list[UUID] | Unset = UNSET
        if _verify_finding_ids is not UNSET:
            verify_finding_ids = []
            for verify_finding_ids_item_data in _verify_finding_ids:
                verify_finding_ids_item = UUID(verify_finding_ids_item_data)

                verify_finding_ids.append(verify_finding_ids_item)

        patch_review_request = cls(
            base_commit_sha=base_commit_sha,
            patch=patch,
            trigger_source=trigger_source,
            verify_finding_ids=verify_finding_ids,
        )

        return patch_review_request
