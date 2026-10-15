from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.refused_environment import RefusedEnvironment


T = TypeVar("T", bound="RunNowRefusalViewType4")


@_attrs_define
class RunNowRefusalViewType4:
    """The environment reviews this repository but is not ready; its own
    account of why, when it has one, is `status_detail`. The
    environment's setup.

       Attributes:
           environment (RefusedEnvironment): An environment a refusal names. `external_key` is how its pages are
                addressed.
           reason (Literal['ENVIRONMENT_NOT_READY']):
           status_detail (None | str | Unset):
    """

    environment: RefusedEnvironment
    reason: Literal["ENVIRONMENT_NOT_READY"]
    status_detail: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        environment = self.environment.to_dict()

        reason = self.reason

        status_detail: None | str | Unset
        if isinstance(self.status_detail, Unset):
            status_detail = UNSET
        else:
            status_detail = self.status_detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "environment": environment,
                "reason": reason,
            }
        )
        if status_detail is not UNSET:
            field_dict["status_detail"] = status_detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.refused_environment import RefusedEnvironment  # noqa: PLC0415

        d = dict(src_dict)
        environment = RefusedEnvironment.from_dict(d.pop("environment"))

        reason = cast(Literal["ENVIRONMENT_NOT_READY"], d.pop("reason"))
        if reason != "ENVIRONMENT_NOT_READY":
            raise ValueError(f"reason must match const 'ENVIRONMENT_NOT_READY', got '{reason}'")

        def _parse_status_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status_detail = _parse_status_detail(d.pop("status_detail", UNSET))

        run_now_refusal_view_type_4 = cls(
            environment=environment,
            reason=reason,
            status_detail=status_detail,
        )

        run_now_refusal_view_type_4.additional_properties = d
        return run_now_refusal_view_type_4

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
