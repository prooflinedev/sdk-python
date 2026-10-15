from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.export_review_kind import ExportReviewKind
from ..models.export_review_status import ExportReviewStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReviewsExportRow")


@_attrs_define
class ReviewsExportRow:
    """The NDJSON row and CSV column contract. Repository names are display data;
    the stable repository ID and recorded commit identify the reviewed input.

       Attributes:
           created_at (datetime.datetime): When the review was created; the export window filters on this time.
           dataset_version (int): The row contract version, always `1`.
           kind (ExportReviewKind):
           organization_id (UUID): The organization that owns the review.
           review_id (UUID): The review's stable ID.
           status (ExportReviewStatus):
           trigger_origin (str): What started the review, derived from its trigger key: `AUTOMATIC`, `COMMAND`,
                `RERUN`, `MANUAL`, or `UNKNOWN` for a key this build does not recognize.
           base_commit_sha (None | str | Unset): The pinned base commit SHA, null when the review records none.
           completed_at (datetime.datetime | None | Unset): When the review finished, null while it has not.
           github_repository_id (int | None | Unset): GitHub's ID for the repository, null when the organization no longer
               owns it or the
                review records no repository.
           head_commit_sha (None | str | Unset): The pinned head commit SHA, null when the review records none.
           pull_request_number (int | None | Unset): The pull request number, null when the review records none, as for a
               deployment.
           repository_full_name (None | str | Unset): The repository's current `owner/name` display name, null when the
               organization no
                longer owns it or the review records no repository.
           repository_id (None | Unset | UUID): The stable ID of the review's primary repository, null when the review
               records none.
           run_number (int | None | Unset): The review's ordinal among the reviews of its pull request, null for a review
               without
                a repository and pull request.
    """

    created_at: datetime.datetime
    dataset_version: int
    kind: ExportReviewKind
    organization_id: UUID
    review_id: UUID
    status: ExportReviewStatus
    trigger_origin: str
    base_commit_sha: None | str | Unset = UNSET
    completed_at: datetime.datetime | None | Unset = UNSET
    github_repository_id: int | None | Unset = UNSET
    head_commit_sha: None | str | Unset = UNSET
    pull_request_number: int | None | Unset = UNSET
    repository_full_name: None | str | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    run_number: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        dataset_version = self.dataset_version

        kind = self.kind.value

        organization_id = str(self.organization_id)

        review_id = str(self.review_id)

        status = self.status.value

        trigger_origin = self.trigger_origin

        base_commit_sha: None | str | Unset
        if isinstance(self.base_commit_sha, Unset):
            base_commit_sha = UNSET
        else:
            base_commit_sha = self.base_commit_sha

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        github_repository_id: int | None | Unset
        if isinstance(self.github_repository_id, Unset):
            github_repository_id = UNSET
        else:
            github_repository_id = self.github_repository_id

        head_commit_sha: None | str | Unset
        if isinstance(self.head_commit_sha, Unset):
            head_commit_sha = UNSET
        else:
            head_commit_sha = self.head_commit_sha

        pull_request_number: int | None | Unset
        if isinstance(self.pull_request_number, Unset):
            pull_request_number = UNSET
        else:
            pull_request_number = self.pull_request_number

        repository_full_name: None | str | Unset
        if isinstance(self.repository_full_name, Unset):
            repository_full_name = UNSET
        else:
            repository_full_name = self.repository_full_name

        repository_id: None | str | Unset
        if isinstance(self.repository_id, Unset):
            repository_id = UNSET
        elif isinstance(self.repository_id, UUID):
            repository_id = str(self.repository_id)
        else:
            repository_id = self.repository_id

        run_number: int | None | Unset
        if isinstance(self.run_number, Unset):
            run_number = UNSET
        else:
            run_number = self.run_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "dataset_version": dataset_version,
                "kind": kind,
                "organization_id": organization_id,
                "review_id": review_id,
                "status": status,
                "trigger_origin": trigger_origin,
            }
        )
        if base_commit_sha is not UNSET:
            field_dict["base_commit_sha"] = base_commit_sha
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if github_repository_id is not UNSET:
            field_dict["github_repository_id"] = github_repository_id
        if head_commit_sha is not UNSET:
            field_dict["head_commit_sha"] = head_commit_sha
        if pull_request_number is not UNSET:
            field_dict["pull_request_number"] = pull_request_number
        if repository_full_name is not UNSET:
            field_dict["repository_full_name"] = repository_full_name
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if run_number is not UNSET:
            field_dict["run_number"] = run_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        dataset_version = d.pop("dataset_version")

        kind = ExportReviewKind(d.pop("kind"))

        organization_id = UUID(d.pop("organization_id"))

        review_id = UUID(d.pop("review_id"))

        status = ExportReviewStatus(d.pop("status"))

        trigger_origin = d.pop("trigger_origin")

        def _parse_base_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_commit_sha = _parse_base_commit_sha(d.pop("base_commit_sha", UNSET))

        def _parse_completed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = datetime.datetime.fromisoformat(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_github_repository_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        github_repository_id = _parse_github_repository_id(d.pop("github_repository_id", UNSET))

        def _parse_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_sha = _parse_head_commit_sha(d.pop("head_commit_sha", UNSET))

        def _parse_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_number = _parse_pull_request_number(d.pop("pull_request_number", UNSET))

        def _parse_repository_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_full_name = _parse_repository_full_name(d.pop("repository_full_name", UNSET))

        def _parse_repository_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repository_id_type_0 = UUID(data)

                return repository_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        repository_id = _parse_repository_id(d.pop("repository_id", UNSET))

        def _parse_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        run_number = _parse_run_number(d.pop("run_number", UNSET))

        reviews_export_row = cls(
            created_at=created_at,
            dataset_version=dataset_version,
            kind=kind,
            organization_id=organization_id,
            review_id=review_id,
            status=status,
            trigger_origin=trigger_origin,
            base_commit_sha=base_commit_sha,
            completed_at=completed_at,
            github_repository_id=github_repository_id,
            head_commit_sha=head_commit_sha,
            pull_request_number=pull_request_number,
            repository_full_name=repository_full_name,
            repository_id=repository_id,
            run_number=run_number,
        )

        reviews_export_row.additional_properties = d
        return reviews_export_row

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
