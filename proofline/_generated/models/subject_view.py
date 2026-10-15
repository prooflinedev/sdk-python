from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subject_authorization import SubjectAuthorization


T = TypeVar("T", bound="SubjectView")


@_attrs_define
class SubjectView:
    """
    Attributes:
        id (UUID): The subject's stable identifier. It holds across a poll refresh even
             when a concurrently populated subject shifts this response's
             `(kind, id)` order: a client keying its own local UI state (an open
             disclosure, a focused control) by array index would otherwise lose
             that state to a reorder that changed nothing it owns.
        kind (str): `GIT_REVISION`, `GIT_PATCH`, `GITHUB_WORKFLOW_RUN`, `ARTIFACT` or `DEPLOYMENT`.
        release_authorizations (list[SubjectAuthorization]): The assessments whose own verified release set authorized
            this
             subject.

             A review with several environments accumulates one subject list, but
             authorization is per assessment: an artifact one environment's read
             authenticated is not evidence for a neighbour whose own read gapped or
             refused. Naming the assessments keeps the union from reading as a
             shared fact.

             Empty for a subject no release-set read produced (the reviewed
             revision, the workflow run, a deployment), because those are the
             review's own coordinates rather than one environment's authenticated
             evidence, not because every environment refused them.
        role (str): `PRIMARY` for the revision under review; `COMPANION` for context read
             from another authenticated repository.
        artifact_digest (None | str | Unset): An immutable OCI digest, never a mutable tag.
        commit_sha (None | str | Unset): The pinned commit of a `GIT_REVISION` subject, or the base commit a
             `GIT_PATCH` subject applies to. Absent for other kinds.
        deployment_external_id (None | str | Unset): The GitHub deployment identifier a `GITHUB_WORKFLOW_RUN` subject
            ran for. Absent when the run was not for a deployment.
        patch_digest (None | str | Unset): The SHA-256 of a `GIT_PATCH` subject's canonical patch. Absent for
             other kinds.
        repository_full_name (None | str | Unset): Absent only when the subject's repository record itself is gone.
        repository_id (None | Unset | UUID): The immutable repository identity of this subject, including companions.
        url (None | str | Unset): The subject on GitHub: the commit for a revision, the run for a
             workflow run. Absent for kinds GitHub does not address (`GIT_PATCH`,
             ARTIFACT, DEPLOYMENT) or when the subject's repository is unknown.
        workflow_attempt (int | None | Unset): The attempt number of a `GITHUB_WORKFLOW_RUN` subject. Absent for other
            kinds.
        workflow_run_id (int | None | Unset): The GitHub Actions run of a `GITHUB_WORKFLOW_RUN` subject. Absent for
            other kinds.
    """

    id: UUID
    kind: str
    release_authorizations: list[SubjectAuthorization]
    role: str
    artifact_digest: None | str | Unset = UNSET
    commit_sha: None | str | Unset = UNSET
    deployment_external_id: None | str | Unset = UNSET
    patch_digest: None | str | Unset = UNSET
    repository_full_name: None | str | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    url: None | str | Unset = UNSET
    workflow_attempt: int | None | Unset = UNSET
    workflow_run_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        kind = self.kind

        release_authorizations = []
        for release_authorizations_item_data in self.release_authorizations:
            release_authorizations_item = release_authorizations_item_data.to_dict()
            release_authorizations.append(release_authorizations_item)

        role = self.role

        artifact_digest: None | str | Unset
        if isinstance(self.artifact_digest, Unset):
            artifact_digest = UNSET
        else:
            artifact_digest = self.artifact_digest

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        deployment_external_id: None | str | Unset
        if isinstance(self.deployment_external_id, Unset):
            deployment_external_id = UNSET
        else:
            deployment_external_id = self.deployment_external_id

        patch_digest: None | str | Unset
        if isinstance(self.patch_digest, Unset):
            patch_digest = UNSET
        else:
            patch_digest = self.patch_digest

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

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        workflow_attempt: int | None | Unset
        if isinstance(self.workflow_attempt, Unset):
            workflow_attempt = UNSET
        else:
            workflow_attempt = self.workflow_attempt

        workflow_run_id: int | None | Unset
        if isinstance(self.workflow_run_id, Unset):
            workflow_run_id = UNSET
        else:
            workflow_run_id = self.workflow_run_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "kind": kind,
                "release_authorizations": release_authorizations,
                "role": role,
            }
        )
        if artifact_digest is not UNSET:
            field_dict["artifact_digest"] = artifact_digest
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if deployment_external_id is not UNSET:
            field_dict["deployment_external_id"] = deployment_external_id
        if patch_digest is not UNSET:
            field_dict["patch_digest"] = patch_digest
        if repository_full_name is not UNSET:
            field_dict["repository_full_name"] = repository_full_name
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if url is not UNSET:
            field_dict["url"] = url
        if workflow_attempt is not UNSET:
            field_dict["workflow_attempt"] = workflow_attempt
        if workflow_run_id is not UNSET:
            field_dict["workflow_run_id"] = workflow_run_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.subject_authorization import SubjectAuthorization  # noqa: PLC0415

        d = dict(src_dict)
        id = UUID(d.pop("id"))

        kind = d.pop("kind")

        release_authorizations = []
        _release_authorizations = d.pop("release_authorizations")
        for release_authorizations_item_data in _release_authorizations:
            release_authorizations_item = SubjectAuthorization.from_dict(
                release_authorizations_item_data
            )

            release_authorizations.append(release_authorizations_item)

        role = d.pop("role")

        def _parse_artifact_digest(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        artifact_digest = _parse_artifact_digest(d.pop("artifact_digest", UNSET))

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_deployment_external_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deployment_external_id = _parse_deployment_external_id(
            d.pop("deployment_external_id", UNSET)
        )

        def _parse_patch_digest(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        patch_digest = _parse_patch_digest(d.pop("patch_digest", UNSET))

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

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_workflow_attempt(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        workflow_attempt = _parse_workflow_attempt(d.pop("workflow_attempt", UNSET))

        def _parse_workflow_run_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        workflow_run_id = _parse_workflow_run_id(d.pop("workflow_run_id", UNSET))

        subject_view = cls(
            id=id,
            kind=kind,
            release_authorizations=release_authorizations,
            role=role,
            artifact_digest=artifact_digest,
            commit_sha=commit_sha,
            deployment_external_id=deployment_external_id,
            patch_digest=patch_digest,
            repository_full_name=repository_full_name,
            repository_id=repository_id,
            url=url,
            workflow_attempt=workflow_attempt,
            workflow_run_id=workflow_run_id,
        )

        subject_view.additional_properties = d
        return subject_view

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
