from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.refused_environment import RefusedEnvironment


T = TypeVar("T", bound="RunNowRefusalViewType3")


@_attrs_define
class RunNowRefusalViewType3:
    """The environment is linked but the link has pull request reviews off:
    the repository's review settings, where environments are chosen.

       Attributes:
           environment (RefusedEnvironment): An environment a refusal names. `external_key` is how its pages are
                addressed.
           reason (Literal['ENVIRONMENT_REVIEWS_OFF']):
    """

    environment: RefusedEnvironment
    reason: Literal["ENVIRONMENT_REVIEWS_OFF"]
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

        reason = cast(Literal["ENVIRONMENT_REVIEWS_OFF"], d.pop("reason"))
        if reason != "ENVIRONMENT_REVIEWS_OFF":
            raise ValueError(f"reason must match const 'ENVIRONMENT_REVIEWS_OFF', got '{reason}'")

        run_now_refusal_view_type_3 = cls(
            environment=environment,
            reason=reason,
        )

        run_now_refusal_view_type_3.additional_properties = d
        return run_now_refusal_view_type_3

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
