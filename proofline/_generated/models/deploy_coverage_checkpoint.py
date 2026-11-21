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
        gaps (list[Literal['AWS_TELEMETRY_CONNECTION_UNAVAILABLE'] | Literal['BASELINE_HELD_REGRESSION'] |
            Literal['BASELINE_UNAVAILABLE'] | Literal['BELOW_TRAFFIC_FLOOR'] | Literal['CHANGE_CHECK_INCOMPLETE'] |
            Literal['CHANGE_CHECK_MISSING'] | Literal['ENVIRONMENT_NOT_CHECKED'] | Literal['NO_SIGNALS_CONFIGURED'] |
            Literal['NO_SIGNALS_FOR_TASK_SERVICES'] | Literal['RUNNING_REVISION_UNKNOWN'] |
            Literal['RUNTIME_ATTESTATIONS_PERMISSION_PENDING'] | Literal['RUNTIME_CAPABILITY_UNQUALIFIED'] |
            Literal['RUNTIME_COMMIT_BINDING_MISSING'] | Literal['RUNTIME_IMAGE_BUILT_EARLIER'] |
            Literal['RUNTIME_INVENTORY_INCOMPLETE'] | Literal['RUNTIME_INVENTORY_STALE'] |
            Literal['RUNTIME_INVENTORY_UNAVAILABLE'] | Literal['RUNTIME_REVISION_UNKNOWN'] |
            Literal['RUNTIME_ROLLOUT_UNSETTLED'] | Literal['RUNTIME_SERVICE_UNKNOWN'] |
            Literal['RUNTIME_TARGET_UNAVAILABLE'] | Literal['RUNTIME_TASK_UNMAPPED'] | Literal['RUNTIME_TRAFFIC_UNKNOWN'] |
            Literal['SIGNAL_BUCKET_UNEXPECTED'] | Literal['SIGNAL_CONFIGURATION_INVALID'] | Literal['SIGNAL_NO_DATA'] |
            Literal['SIGNAL_NOT_SINGLE_SERIES'] | Literal['SIGNAL_PROJECT_NOT_CONNECTED'] | Literal['SIGNAL_READ_PARTIAL'] |
            Literal['SIGNAL_READ_UNAVAILABLE'] | Literal['SIGNAL_RESPONSE_INVALID'] |
            Literal['TELEMETRY_CONNECTION_UNAVAILABLE'] | Literal['TELEMETRY_CREDENTIAL_UNAVAILABLE']] | Unset): The gaps
            this window's check recorded, beside its recorded result;
             empty while no check of this window is recorded. The deploy's `gaps`
             unite those that leave it unproven.
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
    gaps: (
        list[
            Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"]
            | Literal["BASELINE_HELD_REGRESSION"]
            | Literal["BASELINE_UNAVAILABLE"]
            | Literal["BELOW_TRAFFIC_FLOOR"]
            | Literal["CHANGE_CHECK_INCOMPLETE"]
            | Literal["CHANGE_CHECK_MISSING"]
            | Literal["ENVIRONMENT_NOT_CHECKED"]
            | Literal["NO_SIGNALS_CONFIGURED"]
            | Literal["NO_SIGNALS_FOR_TASK_SERVICES"]
            | Literal["RUNNING_REVISION_UNKNOWN"]
            | Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"]
            | Literal["RUNTIME_CAPABILITY_UNQUALIFIED"]
            | Literal["RUNTIME_COMMIT_BINDING_MISSING"]
            | Literal["RUNTIME_IMAGE_BUILT_EARLIER"]
            | Literal["RUNTIME_INVENTORY_INCOMPLETE"]
            | Literal["RUNTIME_INVENTORY_STALE"]
            | Literal["RUNTIME_INVENTORY_UNAVAILABLE"]
            | Literal["RUNTIME_REVISION_UNKNOWN"]
            | Literal["RUNTIME_ROLLOUT_UNSETTLED"]
            | Literal["RUNTIME_SERVICE_UNKNOWN"]
            | Literal["RUNTIME_TARGET_UNAVAILABLE"]
            | Literal["RUNTIME_TASK_UNMAPPED"]
            | Literal["RUNTIME_TRAFFIC_UNKNOWN"]
            | Literal["SIGNAL_BUCKET_UNEXPECTED"]
            | Literal["SIGNAL_CONFIGURATION_INVALID"]
            | Literal["SIGNAL_NO_DATA"]
            | Literal["SIGNAL_NOT_SINGLE_SERIES"]
            | Literal["SIGNAL_PROJECT_NOT_CONNECTED"]
            | Literal["SIGNAL_READ_PARTIAL"]
            | Literal["SIGNAL_READ_UNAVAILABLE"]
            | Literal["SIGNAL_RESPONSE_INVALID"]
            | Literal["TELEMETRY_CONNECTION_UNAVAILABLE"]
            | Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"]
        ]
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

        gaps: (
            list[
                Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"]
                | Literal["BASELINE_HELD_REGRESSION"]
                | Literal["BASELINE_UNAVAILABLE"]
                | Literal["BELOW_TRAFFIC_FLOOR"]
                | Literal["CHANGE_CHECK_INCOMPLETE"]
                | Literal["CHANGE_CHECK_MISSING"]
                | Literal["ENVIRONMENT_NOT_CHECKED"]
                | Literal["NO_SIGNALS_CONFIGURED"]
                | Literal["NO_SIGNALS_FOR_TASK_SERVICES"]
                | Literal["RUNNING_REVISION_UNKNOWN"]
                | Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"]
                | Literal["RUNTIME_CAPABILITY_UNQUALIFIED"]
                | Literal["RUNTIME_COMMIT_BINDING_MISSING"]
                | Literal["RUNTIME_IMAGE_BUILT_EARLIER"]
                | Literal["RUNTIME_INVENTORY_INCOMPLETE"]
                | Literal["RUNTIME_INVENTORY_STALE"]
                | Literal["RUNTIME_INVENTORY_UNAVAILABLE"]
                | Literal["RUNTIME_REVISION_UNKNOWN"]
                | Literal["RUNTIME_ROLLOUT_UNSETTLED"]
                | Literal["RUNTIME_SERVICE_UNKNOWN"]
                | Literal["RUNTIME_TARGET_UNAVAILABLE"]
                | Literal["RUNTIME_TASK_UNMAPPED"]
                | Literal["RUNTIME_TRAFFIC_UNKNOWN"]
                | Literal["SIGNAL_BUCKET_UNEXPECTED"]
                | Literal["SIGNAL_CONFIGURATION_INVALID"]
                | Literal["SIGNAL_NO_DATA"]
                | Literal["SIGNAL_NOT_SINGLE_SERIES"]
                | Literal["SIGNAL_PROJECT_NOT_CONNECTED"]
                | Literal["SIGNAL_READ_PARTIAL"]
                | Literal["SIGNAL_READ_UNAVAILABLE"]
                | Literal["SIGNAL_RESPONSE_INVALID"]
                | Literal["TELEMETRY_CONNECTION_UNAVAILABLE"]
                | Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"]
            ]
            | Unset
        ) = UNSET
        if not isinstance(self.gaps, Unset):
            gaps = []
            for gaps_item_data in self.gaps:
                gaps_item: (
                    Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"]
                    | Literal["BASELINE_HELD_REGRESSION"]
                    | Literal["BASELINE_UNAVAILABLE"]
                    | Literal["BELOW_TRAFFIC_FLOOR"]
                    | Literal["CHANGE_CHECK_INCOMPLETE"]
                    | Literal["CHANGE_CHECK_MISSING"]
                    | Literal["ENVIRONMENT_NOT_CHECKED"]
                    | Literal["NO_SIGNALS_CONFIGURED"]
                    | Literal["NO_SIGNALS_FOR_TASK_SERVICES"]
                    | Literal["RUNNING_REVISION_UNKNOWN"]
                    | Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"]
                    | Literal["RUNTIME_CAPABILITY_UNQUALIFIED"]
                    | Literal["RUNTIME_COMMIT_BINDING_MISSING"]
                    | Literal["RUNTIME_IMAGE_BUILT_EARLIER"]
                    | Literal["RUNTIME_INVENTORY_INCOMPLETE"]
                    | Literal["RUNTIME_INVENTORY_STALE"]
                    | Literal["RUNTIME_INVENTORY_UNAVAILABLE"]
                    | Literal["RUNTIME_REVISION_UNKNOWN"]
                    | Literal["RUNTIME_ROLLOUT_UNSETTLED"]
                    | Literal["RUNTIME_SERVICE_UNKNOWN"]
                    | Literal["RUNTIME_TARGET_UNAVAILABLE"]
                    | Literal["RUNTIME_TASK_UNMAPPED"]
                    | Literal["RUNTIME_TRAFFIC_UNKNOWN"]
                    | Literal["SIGNAL_BUCKET_UNEXPECTED"]
                    | Literal["SIGNAL_CONFIGURATION_INVALID"]
                    | Literal["SIGNAL_NO_DATA"]
                    | Literal["SIGNAL_NOT_SINGLE_SERIES"]
                    | Literal["SIGNAL_PROJECT_NOT_CONNECTED"]
                    | Literal["SIGNAL_READ_PARTIAL"]
                    | Literal["SIGNAL_READ_UNAVAILABLE"]
                    | Literal["SIGNAL_RESPONSE_INVALID"]
                    | Literal["TELEMETRY_CONNECTION_UNAVAILABLE"]
                    | Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"]
                )
                gaps_item = gaps_item_data
                gaps.append(gaps_item)

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
        if gaps is not UNSET:
            field_dict["gaps"] = gaps

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

        _gaps = d.pop("gaps", UNSET)
        gaps: (
            list[
                Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"]
                | Literal["BASELINE_HELD_REGRESSION"]
                | Literal["BASELINE_UNAVAILABLE"]
                | Literal["BELOW_TRAFFIC_FLOOR"]
                | Literal["CHANGE_CHECK_INCOMPLETE"]
                | Literal["CHANGE_CHECK_MISSING"]
                | Literal["ENVIRONMENT_NOT_CHECKED"]
                | Literal["NO_SIGNALS_CONFIGURED"]
                | Literal["NO_SIGNALS_FOR_TASK_SERVICES"]
                | Literal["RUNNING_REVISION_UNKNOWN"]
                | Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"]
                | Literal["RUNTIME_CAPABILITY_UNQUALIFIED"]
                | Literal["RUNTIME_COMMIT_BINDING_MISSING"]
                | Literal["RUNTIME_IMAGE_BUILT_EARLIER"]
                | Literal["RUNTIME_INVENTORY_INCOMPLETE"]
                | Literal["RUNTIME_INVENTORY_STALE"]
                | Literal["RUNTIME_INVENTORY_UNAVAILABLE"]
                | Literal["RUNTIME_REVISION_UNKNOWN"]
                | Literal["RUNTIME_ROLLOUT_UNSETTLED"]
                | Literal["RUNTIME_SERVICE_UNKNOWN"]
                | Literal["RUNTIME_TARGET_UNAVAILABLE"]
                | Literal["RUNTIME_TASK_UNMAPPED"]
                | Literal["RUNTIME_TRAFFIC_UNKNOWN"]
                | Literal["SIGNAL_BUCKET_UNEXPECTED"]
                | Literal["SIGNAL_CONFIGURATION_INVALID"]
                | Literal["SIGNAL_NO_DATA"]
                | Literal["SIGNAL_NOT_SINGLE_SERIES"]
                | Literal["SIGNAL_PROJECT_NOT_CONNECTED"]
                | Literal["SIGNAL_READ_PARTIAL"]
                | Literal["SIGNAL_READ_UNAVAILABLE"]
                | Literal["SIGNAL_RESPONSE_INVALID"]
                | Literal["TELEMETRY_CONNECTION_UNAVAILABLE"]
                | Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"]
            ]
            | Unset
        ) = UNSET
        if _gaps is not UNSET:
            gaps = []
            for gaps_item_data in _gaps:

                def _parse_gaps_item(
                    data: object,
                ) -> (
                    Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"]
                    | Literal["BASELINE_HELD_REGRESSION"]
                    | Literal["BASELINE_UNAVAILABLE"]
                    | Literal["BELOW_TRAFFIC_FLOOR"]
                    | Literal["CHANGE_CHECK_INCOMPLETE"]
                    | Literal["CHANGE_CHECK_MISSING"]
                    | Literal["ENVIRONMENT_NOT_CHECKED"]
                    | Literal["NO_SIGNALS_CONFIGURED"]
                    | Literal["NO_SIGNALS_FOR_TASK_SERVICES"]
                    | Literal["RUNNING_REVISION_UNKNOWN"]
                    | Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"]
                    | Literal["RUNTIME_CAPABILITY_UNQUALIFIED"]
                    | Literal["RUNTIME_COMMIT_BINDING_MISSING"]
                    | Literal["RUNTIME_IMAGE_BUILT_EARLIER"]
                    | Literal["RUNTIME_INVENTORY_INCOMPLETE"]
                    | Literal["RUNTIME_INVENTORY_STALE"]
                    | Literal["RUNTIME_INVENTORY_UNAVAILABLE"]
                    | Literal["RUNTIME_REVISION_UNKNOWN"]
                    | Literal["RUNTIME_ROLLOUT_UNSETTLED"]
                    | Literal["RUNTIME_SERVICE_UNKNOWN"]
                    | Literal["RUNTIME_TARGET_UNAVAILABLE"]
                    | Literal["RUNTIME_TASK_UNMAPPED"]
                    | Literal["RUNTIME_TRAFFIC_UNKNOWN"]
                    | Literal["SIGNAL_BUCKET_UNEXPECTED"]
                    | Literal["SIGNAL_CONFIGURATION_INVALID"]
                    | Literal["SIGNAL_NO_DATA"]
                    | Literal["SIGNAL_NOT_SINGLE_SERIES"]
                    | Literal["SIGNAL_PROJECT_NOT_CONNECTED"]
                    | Literal["SIGNAL_READ_PARTIAL"]
                    | Literal["SIGNAL_READ_UNAVAILABLE"]
                    | Literal["SIGNAL_RESPONSE_INVALID"]
                    | Literal["TELEMETRY_CONNECTION_UNAVAILABLE"]
                    | Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"]
                ):
                    try:
                        if not (type(data) is str and data == "CHANGE_CHECK_MISSING"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_0 = cast(
                            Literal["CHANGE_CHECK_MISSING"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_0
                            != "CHANGE_CHECK_MISSING"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_0 must match const 'CHANGE_CHECK_MISSING', got '{componentsschemas_deploy_verification_gap_type_0}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_0
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "CHANGE_CHECK_INCOMPLETE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_1 = cast(
                            Literal["CHANGE_CHECK_INCOMPLETE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_1
                            != "CHANGE_CHECK_INCOMPLETE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_1 must match const 'CHANGE_CHECK_INCOMPLETE', got '{componentsschemas_deploy_verification_gap_type_1}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "ENVIRONMENT_NOT_CHECKED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_2 = cast(
                            Literal["ENVIRONMENT_NOT_CHECKED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_2
                            != "ENVIRONMENT_NOT_CHECKED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_2 must match const 'ENVIRONMENT_NOT_CHECKED', got '{componentsschemas_deploy_verification_gap_type_2}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_2
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNNING_REVISION_UNKNOWN"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_3 = cast(
                            Literal["RUNNING_REVISION_UNKNOWN"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_3
                            != "RUNNING_REVISION_UNKNOWN"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_3 must match const 'RUNNING_REVISION_UNKNOWN', got '{componentsschemas_deploy_verification_gap_type_3}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_3
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_TARGET_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_4 = cast(
                            Literal["RUNTIME_TARGET_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_4
                            != "RUNTIME_TARGET_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_4 must match const 'RUNTIME_TARGET_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_4}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_4
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_CAPABILITY_UNQUALIFIED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_5 = cast(
                            Literal["RUNTIME_CAPABILITY_UNQUALIFIED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_5
                            != "RUNTIME_CAPABILITY_UNQUALIFIED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_5 must match const 'RUNTIME_CAPABILITY_UNQUALIFIED', got '{componentsschemas_deploy_verification_gap_type_5}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_5
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (
                            type(data) is str and data == "AWS_TELEMETRY_CONNECTION_UNAVAILABLE"
                        ):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_6 = cast(
                            Literal["AWS_TELEMETRY_CONNECTION_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_6
                            != "AWS_TELEMETRY_CONNECTION_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_6 must match const 'AWS_TELEMETRY_CONNECTION_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_6}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_6
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_INVENTORY_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_7 = cast(
                            Literal["RUNTIME_INVENTORY_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_7
                            != "RUNTIME_INVENTORY_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_7 must match const 'RUNTIME_INVENTORY_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_7}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_7
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_INVENTORY_STALE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_8 = cast(
                            Literal["RUNTIME_INVENTORY_STALE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_8
                            != "RUNTIME_INVENTORY_STALE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_8 must match const 'RUNTIME_INVENTORY_STALE', got '{componentsschemas_deploy_verification_gap_type_8}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_8
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_INVENTORY_INCOMPLETE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_9 = cast(
                            Literal["RUNTIME_INVENTORY_INCOMPLETE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_9
                            != "RUNTIME_INVENTORY_INCOMPLETE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_9 must match const 'RUNTIME_INVENTORY_INCOMPLETE', got '{componentsschemas_deploy_verification_gap_type_9}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_9
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_SERVICE_UNKNOWN"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_10 = cast(
                            Literal["RUNTIME_SERVICE_UNKNOWN"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_10
                            != "RUNTIME_SERVICE_UNKNOWN"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_10 must match const 'RUNTIME_SERVICE_UNKNOWN', got '{componentsschemas_deploy_verification_gap_type_10}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_10
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_TRAFFIC_UNKNOWN"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_11 = cast(
                            Literal["RUNTIME_TRAFFIC_UNKNOWN"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_11
                            != "RUNTIME_TRAFFIC_UNKNOWN"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_11 must match const 'RUNTIME_TRAFFIC_UNKNOWN', got '{componentsschemas_deploy_verification_gap_type_11}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_11
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_REVISION_UNKNOWN"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_12 = cast(
                            Literal["RUNTIME_REVISION_UNKNOWN"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_12
                            != "RUNTIME_REVISION_UNKNOWN"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_12 must match const 'RUNTIME_REVISION_UNKNOWN', got '{componentsschemas_deploy_verification_gap_type_12}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_12
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_ROLLOUT_UNSETTLED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_13 = cast(
                            Literal["RUNTIME_ROLLOUT_UNSETTLED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_13
                            != "RUNTIME_ROLLOUT_UNSETTLED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_13 must match const 'RUNTIME_ROLLOUT_UNSETTLED', got '{componentsschemas_deploy_verification_gap_type_13}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_13
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_COMMIT_BINDING_MISSING"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_14 = cast(
                            Literal["RUNTIME_COMMIT_BINDING_MISSING"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_14
                            != "RUNTIME_COMMIT_BINDING_MISSING"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_14 must match const 'RUNTIME_COMMIT_BINDING_MISSING', got '{componentsschemas_deploy_verification_gap_type_14}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_14
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (
                            type(data) is str and data == "RUNTIME_ATTESTATIONS_PERMISSION_PENDING"
                        ):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_15 = cast(
                            Literal["RUNTIME_ATTESTATIONS_PERMISSION_PENDING"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_15
                            != "RUNTIME_ATTESTATIONS_PERMISSION_PENDING"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_15 must match const 'RUNTIME_ATTESTATIONS_PERMISSION_PENDING', got '{componentsschemas_deploy_verification_gap_type_15}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_15
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_IMAGE_BUILT_EARLIER"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_16 = cast(
                            Literal["RUNTIME_IMAGE_BUILT_EARLIER"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_16
                            != "RUNTIME_IMAGE_BUILT_EARLIER"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_16 must match const 'RUNTIME_IMAGE_BUILT_EARLIER', got '{componentsschemas_deploy_verification_gap_type_16}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_16
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "RUNTIME_TASK_UNMAPPED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_17 = cast(
                            Literal["RUNTIME_TASK_UNMAPPED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_17
                            != "RUNTIME_TASK_UNMAPPED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_17 must match const 'RUNTIME_TASK_UNMAPPED', got '{componentsschemas_deploy_verification_gap_type_17}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_17
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "TELEMETRY_CONNECTION_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_18 = cast(
                            Literal["TELEMETRY_CONNECTION_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_18
                            != "TELEMETRY_CONNECTION_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_18 must match const 'TELEMETRY_CONNECTION_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_18}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_18
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "TELEMETRY_CREDENTIAL_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_19 = cast(
                            Literal["TELEMETRY_CREDENTIAL_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_19
                            != "TELEMETRY_CREDENTIAL_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_19 must match const 'TELEMETRY_CREDENTIAL_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_19}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_19
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "NO_SIGNALS_CONFIGURED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_20 = cast(
                            Literal["NO_SIGNALS_CONFIGURED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_20
                            != "NO_SIGNALS_CONFIGURED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_20 must match const 'NO_SIGNALS_CONFIGURED', got '{componentsschemas_deploy_verification_gap_type_20}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_20
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "NO_SIGNALS_FOR_TASK_SERVICES"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_21 = cast(
                            Literal["NO_SIGNALS_FOR_TASK_SERVICES"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_21
                            != "NO_SIGNALS_FOR_TASK_SERVICES"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_21 must match const 'NO_SIGNALS_FOR_TASK_SERVICES', got '{componentsschemas_deploy_verification_gap_type_21}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_21
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_PROJECT_NOT_CONNECTED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_22 = cast(
                            Literal["SIGNAL_PROJECT_NOT_CONNECTED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_22
                            != "SIGNAL_PROJECT_NOT_CONNECTED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_22 must match const 'SIGNAL_PROJECT_NOT_CONNECTED', got '{componentsschemas_deploy_verification_gap_type_22}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_22
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_CONFIGURATION_INVALID"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_23 = cast(
                            Literal["SIGNAL_CONFIGURATION_INVALID"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_23
                            != "SIGNAL_CONFIGURATION_INVALID"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_23 must match const 'SIGNAL_CONFIGURATION_INVALID', got '{componentsschemas_deploy_verification_gap_type_23}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_23
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_RESPONSE_INVALID"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_24 = cast(
                            Literal["SIGNAL_RESPONSE_INVALID"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_24
                            != "SIGNAL_RESPONSE_INVALID"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_24 must match const 'SIGNAL_RESPONSE_INVALID', got '{componentsschemas_deploy_verification_gap_type_24}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_24
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_READ_PARTIAL"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_25 = cast(
                            Literal["SIGNAL_READ_PARTIAL"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_25
                            != "SIGNAL_READ_PARTIAL"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_25 must match const 'SIGNAL_READ_PARTIAL', got '{componentsschemas_deploy_verification_gap_type_25}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_25
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_READ_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_26 = cast(
                            Literal["SIGNAL_READ_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_26
                            != "SIGNAL_READ_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_26 must match const 'SIGNAL_READ_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_26}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_26
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_NO_DATA"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_27 = cast(
                            Literal["SIGNAL_NO_DATA"], data
                        )
                        if componentsschemas_deploy_verification_gap_type_27 != "SIGNAL_NO_DATA":
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_27 must match const 'SIGNAL_NO_DATA', got '{componentsschemas_deploy_verification_gap_type_27}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_27
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_NOT_SINGLE_SERIES"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_28 = cast(
                            Literal["SIGNAL_NOT_SINGLE_SERIES"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_28
                            != "SIGNAL_NOT_SINGLE_SERIES"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_28 must match const 'SIGNAL_NOT_SINGLE_SERIES', got '{componentsschemas_deploy_verification_gap_type_28}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_28
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "SIGNAL_BUCKET_UNEXPECTED"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_29 = cast(
                            Literal["SIGNAL_BUCKET_UNEXPECTED"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_29
                            != "SIGNAL_BUCKET_UNEXPECTED"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_29 must match const 'SIGNAL_BUCKET_UNEXPECTED', got '{componentsschemas_deploy_verification_gap_type_29}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_29
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "BASELINE_UNAVAILABLE"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_30 = cast(
                            Literal["BASELINE_UNAVAILABLE"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_30
                            != "BASELINE_UNAVAILABLE"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_30 must match const 'BASELINE_UNAVAILABLE', got '{componentsschemas_deploy_verification_gap_type_30}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_30
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not (type(data) is str and data == "BELOW_TRAFFIC_FLOOR"):
                            raise TypeError()
                        componentsschemas_deploy_verification_gap_type_31 = cast(
                            Literal["BELOW_TRAFFIC_FLOOR"], data
                        )
                        if (
                            componentsschemas_deploy_verification_gap_type_31
                            != "BELOW_TRAFFIC_FLOOR"
                        ):
                            raise ValueError(
                                f"/components/schemas/DeployVerificationGap_type_31 must match const 'BELOW_TRAFFIC_FLOOR', got '{componentsschemas_deploy_verification_gap_type_31}'"
                            )
                        return componentsschemas_deploy_verification_gap_type_31
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    if not (type(data) is str and data == "BASELINE_HELD_REGRESSION"):
                        raise TypeError()
                    componentsschemas_deploy_verification_gap_type_32 = cast(
                        Literal["BASELINE_HELD_REGRESSION"], data
                    )
                    if (
                        componentsschemas_deploy_verification_gap_type_32
                        != "BASELINE_HELD_REGRESSION"
                    ):
                        raise ValueError(
                            f"/components/schemas/DeployVerificationGap_type_32 must match const 'BASELINE_HELD_REGRESSION', got '{componentsschemas_deploy_verification_gap_type_32}'"
                        )
                    return componentsschemas_deploy_verification_gap_type_32

                gaps_item = _parse_gaps_item(gaps_item_data)

                gaps.append(gaps_item)

        deploy_coverage_checkpoint = cls(
            checkpoint=checkpoint,
            due_at=due_at,
            result=result,
            gaps=gaps,
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
