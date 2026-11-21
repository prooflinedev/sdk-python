from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.deploy_checkpoint import DeployCheckpoint
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeployCoverageCheckpoint")


@_attrs_define
class DeployCoverageCheckpoint:
    """One checkpoint of a verified deploy.

    Attributes:
        checkpoint (DeployCheckpoint): One of the four checks of a deploy.
        due_at (datetime.datetime): When a missing check becomes overdue, allowing the workflow's read
             delay, landing inventory reread, successor wait and transient-read retries.
        result (Literal['HEALTHY'] | Literal['INCOMPLETE'] | Literal['REGRESSED'] | Literal['SUPERSEDED'] | None |
            Unset): The recorded result; absent while no check of this window is recorded.
    """

    checkpoint: DeployCheckpoint
    due_at: datetime.datetime
    result: (
        Literal["HEALTHY"]
        | Literal["INCOMPLETE"]
        | Literal["REGRESSED"]
        | Literal["SUPERSEDED"]
        | None
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        checkpoint = self.checkpoint.value

        due_at = self.due_at.isoformat()

        result: (
            Literal["HEALTHY"]
            | Literal["INCOMPLETE"]
            | Literal["REGRESSED"]
            | Literal["SUPERSEDED"]
            | None
            | Unset
        )
        if isinstance(self.result, Unset):
            result = UNSET
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checkpoint": checkpoint,
                "due_at": due_at,
            }
        )
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        checkpoint = DeployCheckpoint(d.pop("checkpoint"))

        due_at = datetime.datetime.fromisoformat(d.pop("due_at"))

        def _parse_result(
            data: object,
        ) -> (
            Literal["HEALTHY"]
            | Literal["INCOMPLETE"]
            | Literal["REGRESSED"]
            | Literal["SUPERSEDED"]
            | None
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not (type(data) is str and data == "HEALTHY"):
                    raise TypeError()
                componentsschemas_deploy_check_result_type_0 = cast(Literal["HEALTHY"], data)
                if componentsschemas_deploy_check_result_type_0 != "HEALTHY":
                    raise ValueError(
                        f"/components/schemas/DeployCheckResult_type_0 must match const 'HEALTHY', got '{componentsschemas_deploy_check_result_type_0}'"
                    )
                return componentsschemas_deploy_check_result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "REGRESSED"):
                    raise TypeError()
                componentsschemas_deploy_check_result_type_1 = cast(Literal["REGRESSED"], data)
                if componentsschemas_deploy_check_result_type_1 != "REGRESSED":
                    raise ValueError(
                        f"/components/schemas/DeployCheckResult_type_1 must match const 'REGRESSED', got '{componentsschemas_deploy_check_result_type_1}'"
                    )
                return componentsschemas_deploy_check_result_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "SUPERSEDED"):
                    raise TypeError()
                componentsschemas_deploy_check_result_type_2 = cast(Literal["SUPERSEDED"], data)
                if componentsschemas_deploy_check_result_type_2 != "SUPERSEDED":
                    raise ValueError(
                        f"/components/schemas/DeployCheckResult_type_2 must match const 'SUPERSEDED', got '{componentsschemas_deploy_check_result_type_2}'"
                    )
                return componentsschemas_deploy_check_result_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "INCOMPLETE"):
                    raise TypeError()
                componentsschemas_deploy_check_result_type_3 = cast(Literal["INCOMPLETE"], data)
                if componentsschemas_deploy_check_result_type_3 != "INCOMPLETE":
                    raise ValueError(
                        f"/components/schemas/DeployCheckResult_type_3 must match const 'INCOMPLETE', got '{componentsschemas_deploy_check_result_type_3}'"
                    )
                return componentsschemas_deploy_check_result_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["HEALTHY"]
                | Literal["INCOMPLETE"]
                | Literal["REGRESSED"]
                | Literal["SUPERSEDED"]
                | None
                | Unset,
                data,
            )

        result = _parse_result(d.pop("result", UNSET))

        deploy_coverage_checkpoint = cls(
            checkpoint=checkpoint,
            due_at=due_at,
            result=result,
        )

        deploy_coverage_checkpoint.additional_properties = d
        return deploy_coverage_checkpoint

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
