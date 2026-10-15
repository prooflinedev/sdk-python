from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.export_validation import ExportValidation
from ..models.export_validation_source import ExportValidationSource
from ..types import UNSET, Unset

T = TypeVar("T", bound="FindingValidationsExportRow")


@_attrs_define
class FindingValidationsExportRow:
    """One append-only validation, including its recorded actor display metadata.
    Missing historical actors stay absent; the export does not infer identity.

       Attributes:
           created_at (datetime.datetime): When the validation was recorded; the export window filters on this time.
           dataset_version (int): The row contract version, always `1`.
           environment_id (UUID): The environment of the assessment that recorded the finding.
           finding_id (UUID): The finding occurrence the validation applies to.
           organization_id (UUID): The organization that owns the finding.
           review_id (UUID): The review whose assessment recorded the finding.
           source (ExportValidationSource):
           validation (ExportValidation):
           validation_id (UUID): The stable ID of this validation record.
           actor_github_user_id (int | None | Unset): The GitHub user ID captured as the actor, null when none was
               captured.
           actor_login (None | str | Unset): The GitHub login captured as display metadata at validation time, null when
               none was
                captured.
           actor_user_id (None | Unset | UUID): The Proofline user captured as the actor, null when none was captured.
           expires_at (datetime.datetime | None | Unset): When the decision expires, null when it records no expiry.
           repository_id (None | Unset | UUID): The review's primary repository, null when the review records none.
    """

    created_at: datetime.datetime
    dataset_version: int
    environment_id: UUID
    finding_id: UUID
    organization_id: UUID
    review_id: UUID
    source: ExportValidationSource
    validation: ExportValidation
    validation_id: UUID
    actor_github_user_id: int | None | Unset = UNSET
    actor_login: None | str | Unset = UNSET
    actor_user_id: None | Unset | UUID = UNSET
    expires_at: datetime.datetime | None | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        dataset_version = self.dataset_version

        environment_id = str(self.environment_id)

        finding_id = str(self.finding_id)

        organization_id = str(self.organization_id)

        review_id = str(self.review_id)

        source = self.source.value

        validation = self.validation.value

        validation_id = str(self.validation_id)

        actor_github_user_id: int | None | Unset
        if isinstance(self.actor_github_user_id, Unset):
            actor_github_user_id = UNSET
        else:
            actor_github_user_id = self.actor_github_user_id

        actor_login: None | str | Unset
        if isinstance(self.actor_login, Unset):
            actor_login = UNSET
        else:
            actor_login = self.actor_login

        actor_user_id: None | str | Unset
        if isinstance(self.actor_user_id, Unset):
            actor_user_id = UNSET
        elif isinstance(self.actor_user_id, UUID):
            actor_user_id = str(self.actor_user_id)
        else:
            actor_user_id = self.actor_user_id

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        repository_id: None | str | Unset
        if isinstance(self.repository_id, Unset):
            repository_id = UNSET
        elif isinstance(self.repository_id, UUID):
            repository_id = str(self.repository_id)
        else:
            repository_id = self.repository_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "dataset_version": dataset_version,
                "environment_id": environment_id,
                "finding_id": finding_id,
                "organization_id": organization_id,
                "review_id": review_id,
                "source": source,
                "validation": validation,
                "validation_id": validation_id,
            }
        )
        if actor_github_user_id is not UNSET:
            field_dict["actor_github_user_id"] = actor_github_user_id
        if actor_login is not UNSET:
            field_dict["actor_login"] = actor_login
        if actor_user_id is not UNSET:
            field_dict["actor_user_id"] = actor_user_id
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        dataset_version = d.pop("dataset_version")

        environment_id = UUID(d.pop("environment_id"))

        finding_id = UUID(d.pop("finding_id"))

        organization_id = UUID(d.pop("organization_id"))

        review_id = UUID(d.pop("review_id"))

        source = ExportValidationSource(d.pop("source"))

        validation = ExportValidation(d.pop("validation"))

        validation_id = UUID(d.pop("validation_id"))

        def _parse_actor_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        actor_github_user_id = _parse_actor_github_user_id(d.pop("actor_github_user_id", UNSET))

        def _parse_actor_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        actor_login = _parse_actor_login(d.pop("actor_login", UNSET))

        def _parse_actor_user_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                actor_user_id_type_0 = UUID(data)

                return actor_user_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        actor_user_id = _parse_actor_user_id(d.pop("actor_user_id", UNSET))

        def _parse_expires_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = datetime.datetime.fromisoformat(data)

                return expires_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

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

        finding_validations_export_row = cls(
            created_at=created_at,
            dataset_version=dataset_version,
            environment_id=environment_id,
            finding_id=finding_id,
            organization_id=organization_id,
            review_id=review_id,
            source=source,
            validation=validation,
            validation_id=validation_id,
            actor_github_user_id=actor_github_user_id,
            actor_login=actor_login,
            actor_user_id=actor_user_id,
            expires_at=expires_at,
            repository_id=repository_id,
        )

        finding_validations_export_row.additional_properties = d
        return finding_validations_export_row

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
