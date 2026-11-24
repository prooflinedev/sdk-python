from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EnvironmentCheck")


@_attrs_define
class EnvironmentCheck:
    """One environment linked to the reviewed repository, and whether this
    review checked it.

       Attributes:
           environment_display_name (str): The environment's display name.
           environment_external_key (str): The environment's key, which names its console pages.
           state (Literal['CHECKED'] | Literal['CHECKING'] | Literal['NOT_APPLICABLE'] | Literal['NOT_CHECKED']):
           reason (Literal['ENDED'] | Literal['FORK_PULL_REQUEST'] | Literal['NO_CLOUD_ACCOUNT'] | Literal['NOT_COVERED'] |
               Literal['PULL_REQUEST_REVIEWS_OFF'] | Literal['READS_REFUSED'] | Literal['UNFINISHED'] | None | Unset): Why the
               environment was not checked or does not apply. Null when it
                was checked, its check is still running, or
                `reason_unrecorded` is true.
           reason_unrecorded (bool | Unset): True when the review checked nothing in the environment but predates
                Proofline's record of the links its repository had when it was
                created: its repository links the environment by a link made before
                the review, and whether that link then asked for pull request reviews
                is unknown. Absent otherwise.
           unfinished_inventory_incomplete (bool | Unset): True when `reason` is `UNFINISHED` because the assessment's Kian
               pin
                lacked required inventory evidence, so the environment was not
                checked. Absent otherwise, including when the assessment recorded no
                cause.
    """

    environment_display_name: str
    environment_external_key: str
    state: (
        Literal["CHECKED"]
        | Literal["CHECKING"]
        | Literal["NOT_APPLICABLE"]
        | Literal["NOT_CHECKED"]
    )
    reason: (
        Literal["ENDED"]
        | Literal["FORK_PULL_REQUEST"]
        | Literal["NO_CLOUD_ACCOUNT"]
        | Literal["NOT_COVERED"]
        | Literal["PULL_REQUEST_REVIEWS_OFF"]
        | Literal["READS_REFUSED"]
        | Literal["UNFINISHED"]
        | None
        | Unset
    ) = UNSET
    reason_unrecorded: bool | Unset = UNSET
    unfinished_inventory_incomplete: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment_display_name = self.environment_display_name

        environment_external_key = self.environment_external_key

        state: (
            Literal["CHECKED"]
            | Literal["CHECKING"]
            | Literal["NOT_APPLICABLE"]
            | Literal["NOT_CHECKED"]
        )
        state = self.state

        reason: (
            Literal["ENDED"]
            | Literal["FORK_PULL_REQUEST"]
            | Literal["NO_CLOUD_ACCOUNT"]
            | Literal["NOT_COVERED"]
            | Literal["PULL_REQUEST_REVIEWS_OFF"]
            | Literal["READS_REFUSED"]
            | Literal["UNFINISHED"]
            | None
            | Unset
        )
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        reason_unrecorded = self.reason_unrecorded

        unfinished_inventory_incomplete = self.unfinished_inventory_incomplete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment_display_name": environment_display_name,
                "environment_external_key": environment_external_key,
                "state": state,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if reason_unrecorded is not UNSET:
            field_dict["reason_unrecorded"] = reason_unrecorded
        if unfinished_inventory_incomplete is not UNSET:
            field_dict["unfinished_inventory_incomplete"] = unfinished_inventory_incomplete

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        environment_display_name = d.pop("environment_display_name")

        environment_external_key = d.pop("environment_external_key")

        def _parse_state(
            data: object,
        ) -> (
            Literal["CHECKED"]
            | Literal["CHECKING"]
            | Literal["NOT_APPLICABLE"]
            | Literal["NOT_CHECKED"]
        ):
            try:
                if not (type(data) is str and data == "CHECKED"):
                    raise TypeError()
                componentsschemas_environment_check_state_type_0 = cast(Literal["CHECKED"], data)
                if componentsschemas_environment_check_state_type_0 != "CHECKED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckState_type_0 must match const 'CHECKED', got '{componentsschemas_environment_check_state_type_0}'"
                    )
                return componentsschemas_environment_check_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "CHECKING"):
                    raise TypeError()
                componentsschemas_environment_check_state_type_1 = cast(Literal["CHECKING"], data)
                if componentsschemas_environment_check_state_type_1 != "CHECKING":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckState_type_1 must match const 'CHECKING', got '{componentsschemas_environment_check_state_type_1}'"
                    )
                return componentsschemas_environment_check_state_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NOT_CHECKED"):
                    raise TypeError()
                componentsschemas_environment_check_state_type_2 = cast(
                    Literal["NOT_CHECKED"], data
                )
                if componentsschemas_environment_check_state_type_2 != "NOT_CHECKED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckState_type_2 must match const 'NOT_CHECKED', got '{componentsschemas_environment_check_state_type_2}'"
                    )
                return componentsschemas_environment_check_state_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "NOT_APPLICABLE"):
                raise TypeError()
            componentsschemas_environment_check_state_type_3 = cast(Literal["NOT_APPLICABLE"], data)
            if componentsschemas_environment_check_state_type_3 != "NOT_APPLICABLE":
                raise ValueError(
                    f"/components/schemas/EnvironmentCheckState_type_3 must match const 'NOT_APPLICABLE', got '{componentsschemas_environment_check_state_type_3}'"
                )
            return componentsschemas_environment_check_state_type_3

        state = _parse_state(d.pop("state"))

        def _parse_reason(
            data: object,
        ) -> (
            Literal["ENDED"]
            | Literal["FORK_PULL_REQUEST"]
            | Literal["NO_CLOUD_ACCOUNT"]
            | Literal["NOT_COVERED"]
            | Literal["PULL_REQUEST_REVIEWS_OFF"]
            | Literal["READS_REFUSED"]
            | Literal["UNFINISHED"]
            | None
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not (type(data) is str and data == "NOT_COVERED"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_0 = cast(
                    Literal["NOT_COVERED"], data
                )
                if componentsschemas_environment_check_reason_type_0 != "NOT_COVERED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_0 must match const 'NOT_COVERED', got '{componentsschemas_environment_check_reason_type_0}'"
                    )
                return componentsschemas_environment_check_reason_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NO_CLOUD_ACCOUNT"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_1 = cast(
                    Literal["NO_CLOUD_ACCOUNT"], data
                )
                if componentsschemas_environment_check_reason_type_1 != "NO_CLOUD_ACCOUNT":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_1 must match const 'NO_CLOUD_ACCOUNT', got '{componentsschemas_environment_check_reason_type_1}'"
                    )
                return componentsschemas_environment_check_reason_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "READS_REFUSED"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_2 = cast(
                    Literal["READS_REFUSED"], data
                )
                if componentsschemas_environment_check_reason_type_2 != "READS_REFUSED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_2 must match const 'READS_REFUSED', got '{componentsschemas_environment_check_reason_type_2}'"
                    )
                return componentsschemas_environment_check_reason_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "FORK_PULL_REQUEST"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_3 = cast(
                    Literal["FORK_PULL_REQUEST"], data
                )
                if componentsschemas_environment_check_reason_type_3 != "FORK_PULL_REQUEST":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_3 must match const 'FORK_PULL_REQUEST', got '{componentsschemas_environment_check_reason_type_3}'"
                    )
                return componentsschemas_environment_check_reason_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNFINISHED"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_4 = cast(
                    Literal["UNFINISHED"], data
                )
                if componentsschemas_environment_check_reason_type_4 != "UNFINISHED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_4 must match const 'UNFINISHED', got '{componentsschemas_environment_check_reason_type_4}'"
                    )
                return componentsschemas_environment_check_reason_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "ENDED"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_5 = cast(Literal["ENDED"], data)
                if componentsschemas_environment_check_reason_type_5 != "ENDED":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_5 must match const 'ENDED', got '{componentsschemas_environment_check_reason_type_5}'"
                    )
                return componentsschemas_environment_check_reason_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "PULL_REQUEST_REVIEWS_OFF"):
                    raise TypeError()
                componentsschemas_environment_check_reason_type_6 = cast(
                    Literal["PULL_REQUEST_REVIEWS_OFF"], data
                )
                if componentsschemas_environment_check_reason_type_6 != "PULL_REQUEST_REVIEWS_OFF":
                    raise ValueError(
                        f"/components/schemas/EnvironmentCheckReason_type_6 must match const 'PULL_REQUEST_REVIEWS_OFF', got '{componentsschemas_environment_check_reason_type_6}'"
                    )
                return componentsschemas_environment_check_reason_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["ENDED"]
                | Literal["FORK_PULL_REQUEST"]
                | Literal["NO_CLOUD_ACCOUNT"]
                | Literal["NOT_COVERED"]
                | Literal["PULL_REQUEST_REVIEWS_OFF"]
                | Literal["READS_REFUSED"]
                | Literal["UNFINISHED"]
                | None
                | Unset,
                data,
            )

        reason = _parse_reason(d.pop("reason", UNSET))

        reason_unrecorded = d.pop("reason_unrecorded", UNSET)

        unfinished_inventory_incomplete = d.pop("unfinished_inventory_incomplete", UNSET)

        environment_check = cls(
            environment_display_name=environment_display_name,
            environment_external_key=environment_external_key,
            state=state,
            reason=reason,
            reason_unrecorded=reason_unrecorded,
            unfinished_inventory_incomplete=unfinished_inventory_incomplete,
        )

        environment_check.additional_properties = d
        return environment_check

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
