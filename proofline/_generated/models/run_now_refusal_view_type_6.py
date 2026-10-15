from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.refused_environment import RefusedEnvironment


T = TypeVar("T", bound="RunNowRefusalViewType6")


@_attrs_define
class RunNowRefusalViewType6:
    """The environment's active typed revision cannot name one delivery
    target for this repository. The environment's link to the
    repository; absent only if the environment was removed meanwhile.

       Attributes:
           detail (str):
           reason (Literal['INVALID_DELIVERY_CONFIGURATION']):
           environment (None | RefusedEnvironment | Unset):
    """

    detail: str
    reason: Literal["INVALID_DELIVERY_CONFIGURATION"]
    environment: None | RefusedEnvironment | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.refused_environment import RefusedEnvironment  # noqa: PLC0415

        detail = self.detail

        reason = self.reason

        environment: dict[str, Any] | None | Unset
        if isinstance(self.environment, Unset):
            environment = UNSET
        elif isinstance(self.environment, RefusedEnvironment):
            environment = self.environment.to_dict()
        else:
            environment = self.environment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
                "reason": reason,
            }
        )
        if environment is not UNSET:
            field_dict["environment"] = environment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.refused_environment import RefusedEnvironment  # noqa: PLC0415

        d = dict(src_dict)
        detail = d.pop("detail")

        reason = cast(Literal["INVALID_DELIVERY_CONFIGURATION"], d.pop("reason"))
        if reason != "INVALID_DELIVERY_CONFIGURATION":
            raise ValueError(
                f"reason must match const 'INVALID_DELIVERY_CONFIGURATION', got '{reason}'"
            )

        def _parse_environment(data: object) -> None | RefusedEnvironment | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                environment_type_0 = RefusedEnvironment.from_dict(data)

                return environment_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RefusedEnvironment | Unset, data)

        environment = _parse_environment(d.pop("environment", UNSET))

        run_now_refusal_view_type_6 = cls(
            detail=detail,
            reason=reason,
            environment=environment,
        )

        run_now_refusal_view_type_6.additional_properties = d
        return run_now_refusal_view_type_6

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
