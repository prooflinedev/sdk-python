from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.refused_environment import RefusedEnvironment


T = TypeVar("T", bound="RunNowRefusalViewType5")


@_attrs_define
class RunNowRefusalViewType5:
    """The environment is ready and reviews this repository, but no cloud
    connection of its can currently supply evidence: the account is not
    connected, or the connection was revoked or predates the current
    permission manifest. Which one is on the environment's setup.

       Attributes:
           environment (RefusedEnvironment): An environment a refusal names. `external_key` is how its pages are
                addressed.
           reason (Literal['ENVIRONMENT_EVIDENCE_UNAVAILABLE']):
    """

    environment: RefusedEnvironment
    reason: Literal["ENVIRONMENT_EVIDENCE_UNAVAILABLE"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment = self.environment.to_dict()

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment": environment,
                "reason": reason,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.refused_environment import RefusedEnvironment  # noqa: PLC0415

        d = dict(src_dict)
        environment = RefusedEnvironment.from_dict(d.pop("environment"))

        reason = cast(Literal["ENVIRONMENT_EVIDENCE_UNAVAILABLE"], d.pop("reason"))
        if reason != "ENVIRONMENT_EVIDENCE_UNAVAILABLE":
            raise ValueError(
                f"reason must match const 'ENVIRONMENT_EVIDENCE_UNAVAILABLE', got '{reason}'"
            )

        run_now_refusal_view_type_5 = cls(
            environment=environment,
            reason=reason,
        )

        run_now_refusal_view_type_5.additional_properties = d
        return run_now_refusal_view_type_5

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
