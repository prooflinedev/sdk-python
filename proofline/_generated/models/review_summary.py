from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReviewSummary")


@_attrs_define
class ReviewSummary:
    """
    Attributes:
        assessment_count (int): How many environment assessments this review has.
        created_at (datetime.datetime): When the review was created.
        environment_display_names (list[str]): Display names of this review's assessed environments, not current
            repository links.
        finding_count (int): How many findings this review's assessments recorded, across all of them.
        id (UUID): The review's identifier.
        kind (str): `PULL_REQUEST`, `DEPLOYMENT`, `PATCH`, a review of local changes
             sent as a patch, `COMMIT`, a review of pushed commits, or `FILES`,
             complete selected files at one pushed commit.
        public_key (str): The review's stable public address: `rev_` followed by its identifier without hyphens.
        publication (str): Whether the review reached the pull request: `PUBLISHED`, `WITHHELD`,
             `PUBLICATION_REQUESTED` or `PUBLICATION_REFUSED`. A review run from
             Proofline is withheld until somebody publishes it.
        status (str): The review's lifecycle status: `PENDING`, `RUNNING`, `COMPLETED`, `INCOMPLETE`, `FAILED`,
            `SUPERSEDED`, `STOPPED` or `EXCLUDED`.
        trigger_origin (str): Who asked for this review: `AUTOMATIC`, `COMMAND`, `RERUN`, `MANUAL`,
             or `UNKNOWN` for a trigger key this build does not recognise.
        completed_at (datetime.datetime | None | Unset): When the review reached a terminal status. Absent while it is
            still pending or running.
        current_head_commit_sha (None | str | Unset): The pull request's head commit as the latest provider projection
            reports it, which can differ from `head_commit_sha`. Set only on a single-review read, and absent for a
            deployment review or a pull request with no projection.
        head_commit_sha (None | str | Unset): The head commit this review is pinned to. For a patch review, the
             revision ID Proofline derives from its base commit and patch digest,
             which is not a commit. Absent when the review recorded none.
        head_commit_url (None | str | Unset): The exact revision reviewed. A commit URL, never a branch URL: the
             branch moves, the reviewed input does not. Absent for a patch review.
        publication_detail (None | str | Unset): Why a publication was refused, or how one failed. Server text.
        pull_request_author_avatar_url (None | str | Unset): Provider-supplied avatar URL. Login-derived `.png` URLs do
            not work for
             GitHub App bot accounts and are not portable across GitHub hosts.
        pull_request_author_github_user_id (int | None | Unset): The author's stable GitHub user id: identity for
            profile lookups,
             never display text. Absent when GitHub named no author.
        pull_request_author_login (None | str | Unset): Provider display metadata for the pull request author, not the
            rerun requester.
        pull_request_author_url (None | str | Unset): The author's profile on the deployment's GitHub host. Absent when
            no author login is known.
        pull_request_number (int | None | Unset): The pull request number. Absent for a deployment or patch review.
        pull_request_state (None | str | Unset): Current provider state of the pull request: `OPEN`, `CLOSED`, or
             `MERGED`. Absent for deployment reviews or a missing projection.
        pull_request_title (None | str | Unset): The pull request's title as provider state last reported it, so it
             names the change rather than only numbering it. Untrusted text:
             renderers must treat it as text, never markup.
        pull_request_url (None | str | Unset): The pull request on GitHub. Absent for a deployment review or when the
            repository is unknown.
        repository_full_name (None | str | Unset): The repository's `owner/name`. Absent when the review names no
            repository.
        repository_id (None | Unset | UUID): The review's repository. Set only on a single-review read, and absent there
            when the review names no repository.
        repository_name (None | str | Unset): The repository's name within its owner. Absent when the review names no
            repository.
        repository_url (None | str | Unset): The repository on GitHub. Absent when the deployment's web base
             cannot be joined with the stored name.
        run_number (int | None | Unset): One-based, append-only ordinal within one repository pull request.
    """

    assessment_count: int
    created_at: datetime.datetime
    environment_display_names: list[str]
    finding_count: int
    id: UUID
    kind: str
    public_key: str
    publication: str
    status: str
    trigger_origin: str
    completed_at: datetime.datetime | None | Unset = UNSET
    current_head_commit_sha: None | str | Unset = UNSET
    head_commit_sha: None | str | Unset = UNSET
    head_commit_url: None | str | Unset = UNSET
    publication_detail: None | str | Unset = UNSET
    pull_request_author_avatar_url: None | str | Unset = UNSET
    pull_request_author_github_user_id: int | None | Unset = UNSET
    pull_request_author_login: None | str | Unset = UNSET
    pull_request_author_url: None | str | Unset = UNSET
    pull_request_number: int | None | Unset = UNSET
    pull_request_state: None | str | Unset = UNSET
    pull_request_title: None | str | Unset = UNSET
    pull_request_url: None | str | Unset = UNSET
    repository_full_name: None | str | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    repository_name: None | str | Unset = UNSET
    repository_url: None | str | Unset = UNSET
    run_number: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessment_count = self.assessment_count

        created_at = self.created_at.isoformat()

        environment_display_names = self.environment_display_names

        finding_count = self.finding_count

        id = str(self.id)

        kind = self.kind

        public_key = self.public_key

        publication = self.publication

        status = self.status

        trigger_origin = self.trigger_origin

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        current_head_commit_sha: None | str | Unset
        if isinstance(self.current_head_commit_sha, Unset):
            current_head_commit_sha = UNSET
        else:
            current_head_commit_sha = self.current_head_commit_sha

        head_commit_sha: None | str | Unset
        if isinstance(self.head_commit_sha, Unset):
            head_commit_sha = UNSET
        else:
            head_commit_sha = self.head_commit_sha

        head_commit_url: None | str | Unset
        if isinstance(self.head_commit_url, Unset):
            head_commit_url = UNSET
        else:
            head_commit_url = self.head_commit_url

        publication_detail: None | str | Unset
        if isinstance(self.publication_detail, Unset):
            publication_detail = UNSET
        else:
            publication_detail = self.publication_detail

        pull_request_author_avatar_url: None | str | Unset
        if isinstance(self.pull_request_author_avatar_url, Unset):
            pull_request_author_avatar_url = UNSET
        else:
            pull_request_author_avatar_url = self.pull_request_author_avatar_url

        pull_request_author_github_user_id: int | None | Unset
        if isinstance(self.pull_request_author_github_user_id, Unset):
            pull_request_author_github_user_id = UNSET
        else:
            pull_request_author_github_user_id = self.pull_request_author_github_user_id

        pull_request_author_login: None | str | Unset
        if isinstance(self.pull_request_author_login, Unset):
            pull_request_author_login = UNSET
        else:
            pull_request_author_login = self.pull_request_author_login

        pull_request_author_url: None | str | Unset
        if isinstance(self.pull_request_author_url, Unset):
            pull_request_author_url = UNSET
        else:
            pull_request_author_url = self.pull_request_author_url

        pull_request_number: int | None | Unset
        if isinstance(self.pull_request_number, Unset):
            pull_request_number = UNSET
        else:
            pull_request_number = self.pull_request_number

        pull_request_state: None | str | Unset
        if isinstance(self.pull_request_state, Unset):
            pull_request_state = UNSET
        else:
            pull_request_state = self.pull_request_state

        pull_request_title: None | str | Unset
        if isinstance(self.pull_request_title, Unset):
            pull_request_title = UNSET
        else:
            pull_request_title = self.pull_request_title

        pull_request_url: None | str | Unset
        if isinstance(self.pull_request_url, Unset):
            pull_request_url = UNSET
        else:
            pull_request_url = self.pull_request_url

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

        repository_name: None | str | Unset
        if isinstance(self.repository_name, Unset):
            repository_name = UNSET
        else:
            repository_name = self.repository_name

        repository_url: None | str | Unset
        if isinstance(self.repository_url, Unset):
            repository_url = UNSET
        else:
            repository_url = self.repository_url

        run_number: int | None | Unset
        if isinstance(self.run_number, Unset):
            run_number = UNSET
        else:
            run_number = self.run_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessment_count": assessment_count,
                "created_at": created_at,
                "environment_display_names": environment_display_names,
                "finding_count": finding_count,
                "id": id,
                "kind": kind,
                "public_key": public_key,
                "publication": publication,
                "status": status,
                "trigger_origin": trigger_origin,
            }
        )
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if current_head_commit_sha is not UNSET:
            field_dict["current_head_commit_sha"] = current_head_commit_sha
        if head_commit_sha is not UNSET:
            field_dict["head_commit_sha"] = head_commit_sha
        if head_commit_url is not UNSET:
            field_dict["head_commit_url"] = head_commit_url
        if publication_detail is not UNSET:
            field_dict["publication_detail"] = publication_detail
        if pull_request_author_avatar_url is not UNSET:
            field_dict["pull_request_author_avatar_url"] = pull_request_author_avatar_url
        if pull_request_author_github_user_id is not UNSET:
            field_dict["pull_request_author_github_user_id"] = pull_request_author_github_user_id
        if pull_request_author_login is not UNSET:
            field_dict["pull_request_author_login"] = pull_request_author_login
        if pull_request_author_url is not UNSET:
            field_dict["pull_request_author_url"] = pull_request_author_url
        if pull_request_number is not UNSET:
            field_dict["pull_request_number"] = pull_request_number
        if pull_request_state is not UNSET:
            field_dict["pull_request_state"] = pull_request_state
        if pull_request_title is not UNSET:
            field_dict["pull_request_title"] = pull_request_title
        if pull_request_url is not UNSET:
            field_dict["pull_request_url"] = pull_request_url
        if repository_full_name is not UNSET:
            field_dict["repository_full_name"] = repository_full_name
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name
        if repository_url is not UNSET:
            field_dict["repository_url"] = repository_url
        if run_number is not UNSET:
            field_dict["run_number"] = run_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        assessment_count = d.pop("assessment_count")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        environment_display_names = cast(list[str], d.pop("environment_display_names"))

        finding_count = d.pop("finding_count")

        id = UUID(d.pop("id"))

        kind = d.pop("kind")

        public_key = d.pop("public_key")

        publication = d.pop("publication")

        status = d.pop("status")

        trigger_origin = d.pop("trigger_origin")

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

        def _parse_current_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        current_head_commit_sha = _parse_current_head_commit_sha(
            d.pop("current_head_commit_sha", UNSET)
        )

        def _parse_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_sha = _parse_head_commit_sha(d.pop("head_commit_sha", UNSET))

        def _parse_head_commit_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_url = _parse_head_commit_url(d.pop("head_commit_url", UNSET))

        def _parse_publication_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        publication_detail = _parse_publication_detail(d.pop("publication_detail", UNSET))

        def _parse_pull_request_author_avatar_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_avatar_url = _parse_pull_request_author_avatar_url(
            d.pop("pull_request_author_avatar_url", UNSET)
        )

        def _parse_pull_request_author_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_author_github_user_id = _parse_pull_request_author_github_user_id(
            d.pop("pull_request_author_github_user_id", UNSET)
        )

        def _parse_pull_request_author_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_login = _parse_pull_request_author_login(
            d.pop("pull_request_author_login", UNSET)
        )

        def _parse_pull_request_author_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_url = _parse_pull_request_author_url(
            d.pop("pull_request_author_url", UNSET)
        )

        def _parse_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_number = _parse_pull_request_number(d.pop("pull_request_number", UNSET))

        def _parse_pull_request_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_state = _parse_pull_request_state(d.pop("pull_request_state", UNSET))

        def _parse_pull_request_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_title = _parse_pull_request_title(d.pop("pull_request_title", UNSET))

        def _parse_pull_request_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_url = _parse_pull_request_url(d.pop("pull_request_url", UNSET))

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

        def _parse_repository_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_name = _parse_repository_name(d.pop("repository_name", UNSET))

        def _parse_repository_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_url = _parse_repository_url(d.pop("repository_url", UNSET))

        def _parse_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        run_number = _parse_run_number(d.pop("run_number", UNSET))

        review_summary = cls(
            assessment_count=assessment_count,
            created_at=created_at,
            environment_display_names=environment_display_names,
            finding_count=finding_count,
            id=id,
            kind=kind,
            public_key=public_key,
            publication=publication,
            status=status,
            trigger_origin=trigger_origin,
            completed_at=completed_at,
            current_head_commit_sha=current_head_commit_sha,
            head_commit_sha=head_commit_sha,
            head_commit_url=head_commit_url,
            publication_detail=publication_detail,
            pull_request_author_avatar_url=pull_request_author_avatar_url,
            pull_request_author_github_user_id=pull_request_author_github_user_id,
            pull_request_author_login=pull_request_author_login,
            pull_request_author_url=pull_request_author_url,
            pull_request_number=pull_request_number,
            pull_request_state=pull_request_state,
            pull_request_title=pull_request_title,
            pull_request_url=pull_request_url,
            repository_full_name=repository_full_name,
            repository_id=repository_id,
            repository_name=repository_name,
            repository_url=repository_url,
            run_number=run_number,
        )

        review_summary.additional_properties = d
        return review_summary

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
