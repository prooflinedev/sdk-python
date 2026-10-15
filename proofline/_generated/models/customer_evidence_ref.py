from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomerEvidenceRef")


@_attrs_define
class CustomerEvidenceRef:
    """
    Attributes:
        kind (str): The reference's kind: `repository_file`, `companion_repository_file`,
             `commit`, `workflow_run`, `world_entity`, `deterministic_test`,
             `recorded_read`, `sandbox_experiment`, `vendor_documentation` or
             `text`.
        label (str): The reference's display label, such as a path with its line range. A
             recorded read, a vendor documentation read or an unnamed World entity
             carries a fixed label, and a deterministic test carries its check's
             readable name.
        provenance_status (str): How the reference was obtained: `VERIFIED_REPOSITORY_READ`,
             `PINNED_WORLD_ENTITY`, `EXECUTED_DETERMINISTIC_TEST`,
             `EXECUTED_SANDBOX_EXPERIMENT`, `PROVIDER_REFERENCE`, `RECORDED_READ`
             or `LEGACY_UNSTRUCTURED`.
        commit_sha (None | str | Unset): The commit a file or commit reference reads. Null for other kinds, and
             for a file reference whose review recorded no head commit.
        companion_repository (None | str | Unset): The repository a `companion_repository_file` reference reads from.
             Null for every other kind.
        end_line (int | None | Unset): The last cited line of a file reference. Null when the reference names
             no end line or is not a file reference.
        file_sha256 (None | str | Unset): SHA256 of the complete original file bytes retained by a trusted ENV
             or CODE read. Absent on older references and partial reads.
        legacy_text (None | str | Unset): The unstructured text of a `text` reference. Null for structured
             references and for recorded reads.
        repository_path (None | str | Unset): The cited file's path for a file reference. Null for every other kind.
        start_line (int | None | Unset): The first cited line of a file reference. Null when the reference cites
             no line or is not a file reference.
        url (None | str | Unset): The link the reference resolves to. Null when it resolves to none or
             the review's repository or head commit is unknown.
        workflow_attempt (int | None | Unset): The run attempt of a `workflow_run` reference. Null when the reference
             names no attempt or is another kind.
        workflow_run_id (int | None | Unset): The GitHub Actions run ID of a `workflow_run` reference. Null for every
             other kind.
    """

    kind: str
    label: str
    provenance_status: str
    commit_sha: None | str | Unset = UNSET
    companion_repository: None | str | Unset = UNSET
    end_line: int | None | Unset = UNSET
    file_sha256: None | str | Unset = UNSET
    legacy_text: None | str | Unset = UNSET
    repository_path: None | str | Unset = UNSET
    start_line: int | None | Unset = UNSET
    url: None | str | Unset = UNSET
    workflow_attempt: int | None | Unset = UNSET
    workflow_run_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        label = self.label

        provenance_status = self.provenance_status

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        companion_repository: None | str | Unset
        if isinstance(self.companion_repository, Unset):
            companion_repository = UNSET
        else:
            companion_repository = self.companion_repository

        end_line: int | None | Unset
        if isinstance(self.end_line, Unset):
            end_line = UNSET
        else:
            end_line = self.end_line

        file_sha256: None | str | Unset
        if isinstance(self.file_sha256, Unset):
            file_sha256 = UNSET
        else:
            file_sha256 = self.file_sha256

        legacy_text: None | str | Unset
        if isinstance(self.legacy_text, Unset):
            legacy_text = UNSET
        else:
            legacy_text = self.legacy_text

        repository_path: None | str | Unset
        if isinstance(self.repository_path, Unset):
            repository_path = UNSET
        else:
            repository_path = self.repository_path

        start_line: int | None | Unset
        if isinstance(self.start_line, Unset):
            start_line = UNSET
        else:
            start_line = self.start_line

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
                "kind": kind,
                "label": label,
                "provenance_status": provenance_status,
            }
        )
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if companion_repository is not UNSET:
            field_dict["companion_repository"] = companion_repository
        if end_line is not UNSET:
            field_dict["end_line"] = end_line
        if file_sha256 is not UNSET:
            field_dict["file_sha256"] = file_sha256
        if legacy_text is not UNSET:
            field_dict["legacy_text"] = legacy_text
        if repository_path is not UNSET:
            field_dict["repository_path"] = repository_path
        if start_line is not UNSET:
            field_dict["start_line"] = start_line
        if url is not UNSET:
            field_dict["url"] = url
        if workflow_attempt is not UNSET:
            field_dict["workflow_attempt"] = workflow_attempt
        if workflow_run_id is not UNSET:
            field_dict["workflow_run_id"] = workflow_run_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = d.pop("kind")

        label = d.pop("label")

        provenance_status = d.pop("provenance_status")

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_companion_repository(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        companion_repository = _parse_companion_repository(d.pop("companion_repository", UNSET))

        def _parse_end_line(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        end_line = _parse_end_line(d.pop("end_line", UNSET))

        def _parse_file_sha256(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_sha256 = _parse_file_sha256(d.pop("file_sha256", UNSET))

        def _parse_legacy_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        legacy_text = _parse_legacy_text(d.pop("legacy_text", UNSET))

        def _parse_repository_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_path = _parse_repository_path(d.pop("repository_path", UNSET))

        def _parse_start_line(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        start_line = _parse_start_line(d.pop("start_line", UNSET))

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

        customer_evidence_ref = cls(
            kind=kind,
            label=label,
            provenance_status=provenance_status,
            commit_sha=commit_sha,
            companion_repository=companion_repository,
            end_line=end_line,
            file_sha256=file_sha256,
            legacy_text=legacy_text,
            repository_path=repository_path,
            start_line=start_line,
            url=url,
            workflow_attempt=workflow_attempt,
            workflow_run_id=workflow_run_id,
        )

        customer_evidence_ref.additional_properties = d
        return customer_evidence_ref

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
