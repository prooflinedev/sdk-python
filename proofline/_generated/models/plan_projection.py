from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.assessment_projection import AssessmentProjection
    from ..models.file_projection import FileProjection


T = TypeVar("T", bound="PlanProjection")


@_attrs_define
class PlanProjection:
    """
    Attributes:
        assessments (list[AssessmentProjection]): Environment assessment bindings recorded in the plan.
        base_sha (str): Base commit pinned by the change digest.
        change_digest_sha256 (str): Digest of the exact retained change input.
        fallback_causes (list[str]): Safe codes for fallback causes. Unrecognized values are never echoed.
        files (list[FileProjection]): File routing facts recorded in the plan.
        head_sha (str): Head commit pinned by the change digest.
        repository_id (UUID): Repository named by the validated immutable plan.
    """

    assessments: list[AssessmentProjection]
    base_sha: str
    change_digest_sha256: str
    fallback_causes: list[str]
    files: list[FileProjection]
    head_sha: str
    repository_id: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assessments = []
        for assessments_item_data in self.assessments:
            assessments_item = assessments_item_data.to_dict()
            assessments.append(assessments_item)

        base_sha = self.base_sha

        change_digest_sha256 = self.change_digest_sha256

        fallback_causes = self.fallback_causes

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        head_sha = self.head_sha

        repository_id = str(self.repository_id)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "assessments": assessments,
                "base_sha": base_sha,
                "change_digest_sha256": change_digest_sha256,
                "fallback_causes": fallback_causes,
                "files": files,
                "head_sha": head_sha,
                "repository_id": repository_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assessment_projection import AssessmentProjection  # noqa: PLC0415
        from ..models.file_projection import FileProjection  # noqa: PLC0415

        d = dict(src_dict)
        assessments = []
        _assessments = d.pop("assessments")
        for assessments_item_data in _assessments:
            assessments_item = AssessmentProjection.from_dict(assessments_item_data)

            assessments.append(assessments_item)

        base_sha = d.pop("base_sha")

        change_digest_sha256 = d.pop("change_digest_sha256")

        fallback_causes = cast(list[str], d.pop("fallback_causes"))

        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = FileProjection.from_dict(files_item_data)

            files.append(files_item)

        head_sha = d.pop("head_sha")

        repository_id = UUID(d.pop("repository_id"))

        plan_projection = cls(
            assessments=assessments,
            base_sha=base_sha,
            change_digest_sha256=change_digest_sha256,
            fallback_causes=fallback_causes,
            files=files,
            head_sha=head_sha,
            repository_id=repository_id,
        )

        plan_projection.additional_properties = d
        return plan_projection

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
