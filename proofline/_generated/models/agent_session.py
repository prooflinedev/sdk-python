from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agent_vendor import AgentVendor
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_session_target import AgentSessionTarget


T = TypeVar("T", bound="AgentSession")


@_attrs_define
class AgentSession:
    """
    Attributes:
        attempt (int): This session's place among the finding series' sessions at this
             commit, at most 3.
        connection_id (UUID): The vendor connection the session was started with.
        created_at (datetime.datetime): When the session was requested.
        done (bool): Whether Proofline stopped following the session.
        finding_id (UUID): The finding the session works on.
        id (UUID): The session's ID.
        requested_by_user_id (UUID): The person who started the session.
        review_id (UUID): The review that recorded the finding.
        status (str): `REQUESTED` until the workflow records a status, then `STARTING`,
             `RUNNING`, `FINISHED`, `FAILED`, `REFUSED`, `HEAD_MOVED` or
             `UNKNOWN`.
        target (AgentSessionTarget): What a session is pinned to: the finding's own reviewed pull request.
        updated_at (datetime.datetime): When the session's latest status was recorded.
        vendor (AgentVendor):
        cause (None | str | Unset): Why Proofline ended or refused the session, as a closed code.
        observed_head_sha (None | str | Unset): The pull request's head when it had moved past the reviewed commit,
             for a `HEAD_MOVED` session.
        pull_request_url (None | str | Unset): The pull request the vendor opened, once GitHub confirmed it belongs
             to the target repository.
        untrusted_vendor_summary (None | str | Unset): The vendor's summary: untrusted text, never acted on.
        vendor_status (None | str | Unset): The vendor's own status token.
        vendor_url (None | str | Unset): The session in the vendor's console.
    """

    attempt: int
    connection_id: UUID
    created_at: datetime.datetime
    done: bool
    finding_id: UUID
    id: UUID
    requested_by_user_id: UUID
    review_id: UUID
    status: str
    target: AgentSessionTarget
    updated_at: datetime.datetime
    vendor: AgentVendor
    cause: None | str | Unset = UNSET
    observed_head_sha: None | str | Unset = UNSET
    pull_request_url: None | str | Unset = UNSET
    untrusted_vendor_summary: None | str | Unset = UNSET
    vendor_status: None | str | Unset = UNSET
    vendor_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attempt = self.attempt

        connection_id = str(self.connection_id)

        created_at = self.created_at.isoformat()

        done = self.done

        finding_id = str(self.finding_id)

        id = str(self.id)

        requested_by_user_id = str(self.requested_by_user_id)

        review_id = str(self.review_id)

        status = self.status

        target = self.target.to_dict()

        updated_at = self.updated_at.isoformat()

        vendor = self.vendor.value

        cause: None | str | Unset
        if isinstance(self.cause, Unset):
            cause = UNSET
        else:
            cause = self.cause

        observed_head_sha: None | str | Unset
        if isinstance(self.observed_head_sha, Unset):
            observed_head_sha = UNSET
        else:
            observed_head_sha = self.observed_head_sha

        pull_request_url: None | str | Unset
        if isinstance(self.pull_request_url, Unset):
            pull_request_url = UNSET
        else:
            pull_request_url = self.pull_request_url

        untrusted_vendor_summary: None | str | Unset
        if isinstance(self.untrusted_vendor_summary, Unset):
            untrusted_vendor_summary = UNSET
        else:
            untrusted_vendor_summary = self.untrusted_vendor_summary

        vendor_status: None | str | Unset
        if isinstance(self.vendor_status, Unset):
            vendor_status = UNSET
        else:
            vendor_status = self.vendor_status

        vendor_url: None | str | Unset
        if isinstance(self.vendor_url, Unset):
            vendor_url = UNSET
        else:
            vendor_url = self.vendor_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attempt": attempt,
                "connection_id": connection_id,
                "created_at": created_at,
                "done": done,
                "finding_id": finding_id,
                "id": id,
                "requested_by_user_id": requested_by_user_id,
                "review_id": review_id,
                "status": status,
                "target": target,
                "updated_at": updated_at,
                "vendor": vendor,
            }
        )
        if cause is not UNSET:
            field_dict["cause"] = cause
        if observed_head_sha is not UNSET:
            field_dict["observed_head_sha"] = observed_head_sha
        if pull_request_url is not UNSET:
            field_dict["pull_request_url"] = pull_request_url
        if untrusted_vendor_summary is not UNSET:
            field_dict["untrusted_vendor_summary"] = untrusted_vendor_summary
        if vendor_status is not UNSET:
            field_dict["vendor_status"] = vendor_status
        if vendor_url is not UNSET:
            field_dict["vendor_url"] = vendor_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_session_target import AgentSessionTarget  # noqa: PLC0415

        d = dict(src_dict)
        attempt = d.pop("attempt")

        connection_id = UUID(d.pop("connection_id"))

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        done = d.pop("done")

        finding_id = UUID(d.pop("finding_id"))

        id = UUID(d.pop("id"))

        requested_by_user_id = UUID(d.pop("requested_by_user_id"))

        review_id = UUID(d.pop("review_id"))

        status = d.pop("status")

        target = AgentSessionTarget.from_dict(d.pop("target"))

        updated_at = datetime.datetime.fromisoformat(d.pop("updated_at"))

        vendor = AgentVendor(d.pop("vendor"))

        def _parse_cause(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cause = _parse_cause(d.pop("cause", UNSET))

        def _parse_observed_head_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        observed_head_sha = _parse_observed_head_sha(d.pop("observed_head_sha", UNSET))

        def _parse_pull_request_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_url = _parse_pull_request_url(d.pop("pull_request_url", UNSET))

        def _parse_untrusted_vendor_summary(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        untrusted_vendor_summary = _parse_untrusted_vendor_summary(
            d.pop("untrusted_vendor_summary", UNSET)
        )

        def _parse_vendor_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        vendor_status = _parse_vendor_status(d.pop("vendor_status", UNSET))

        def _parse_vendor_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        vendor_url = _parse_vendor_url(d.pop("vendor_url", UNSET))

        agent_session = cls(
            attempt=attempt,
            connection_id=connection_id,
            created_at=created_at,
            done=done,
            finding_id=finding_id,
            id=id,
            requested_by_user_id=requested_by_user_id,
            review_id=review_id,
            status=status,
            target=target,
            updated_at=updated_at,
            vendor=vendor,
            cause=cause,
            observed_head_sha=observed_head_sha,
            pull_request_url=pull_request_url,
            untrusted_vendor_summary=untrusted_vendor_summary,
            vendor_status=vendor_status,
            vendor_url=vendor_url,
        )

        agent_session.additional_properties = d
        return agent_session

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
