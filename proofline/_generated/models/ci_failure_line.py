from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ci_failure_attribution import CiFailureAttribution
from ..types import UNSET, Unset

T = TypeVar("T", bound="CiFailureLine")


@_attrs_define
class CiFailureLine:
    """One failed CI job as the Check states it.

    Attributes:
        attribution (CiFailureAttribution): What the control plane records as a failure's cause.
        job_name (str): The job's name as the diagnosis admitted it: masked, or `<withheld>`.
             A protected value of the observing review reads as the withheld
             marker.
        run_attempt (int): The GitHub Actions run attempt the job failed in, from 1. The line
             is the newest diagnosed attempt of its run.
        timed_out (bool): Whether the job timed out rather than failed.
        failed_step (None | str | Unset): The first failed step's name, admitted the same way. Null when no
             step concluded as failed.
        undiagnosed (Literal['DECISION_UNAVAILABLE'] | Literal['LOG_NOT_ADMITTED'] | Literal['LOG_TOO_LARGE'] |
            Literal['LOG_UNAVAILABLE'] | Literal['SHADOW'] | Literal['UNDETERMINED'] | None | Unset): Why the failure was
            not diagnosed. Set exactly when `attribution` is
             `UNKNOWN`.
    """

    attribution: CiFailureAttribution
    job_name: str
    run_attempt: int
    timed_out: bool
    failed_step: None | str | Unset = UNSET
    undiagnosed: (
        Literal["DECISION_UNAVAILABLE"]
        | Literal["LOG_NOT_ADMITTED"]
        | Literal["LOG_TOO_LARGE"]
        | Literal["LOG_UNAVAILABLE"]
        | Literal["SHADOW"]
        | Literal["UNDETERMINED"]
        | None
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        attribution = self.attribution.value

        job_name = self.job_name

        run_attempt = self.run_attempt

        timed_out = self.timed_out

        failed_step: None | str | Unset
        if isinstance(self.failed_step, Unset):
            failed_step = UNSET
        else:
            failed_step = self.failed_step

        undiagnosed: (
            Literal["DECISION_UNAVAILABLE"]
            | Literal["LOG_NOT_ADMITTED"]
            | Literal["LOG_TOO_LARGE"]
            | Literal["LOG_UNAVAILABLE"]
            | Literal["SHADOW"]
            | Literal["UNDETERMINED"]
            | None
            | Unset
        )
        if isinstance(self.undiagnosed, Unset):
            undiagnosed = UNSET
        else:
            undiagnosed = self.undiagnosed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attribution": attribution,
                "job_name": job_name,
                "run_attempt": run_attempt,
                "timed_out": timed_out,
            }
        )
        if failed_step is not UNSET:
            field_dict["failed_step"] = failed_step
        if undiagnosed is not UNSET:
            field_dict["undiagnosed"] = undiagnosed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        attribution = CiFailureAttribution(d.pop("attribution"))

        job_name = d.pop("job_name")

        run_attempt = d.pop("run_attempt")

        timed_out = d.pop("timed_out")

        def _parse_failed_step(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        failed_step = _parse_failed_step(d.pop("failed_step", UNSET))

        def _parse_undiagnosed(
            data: object,
        ) -> (
            Literal["DECISION_UNAVAILABLE"]
            | Literal["LOG_NOT_ADMITTED"]
            | Literal["LOG_TOO_LARGE"]
            | Literal["LOG_UNAVAILABLE"]
            | Literal["SHADOW"]
            | Literal["UNDETERMINED"]
            | None
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not (type(data) is str and data == "LOG_UNAVAILABLE"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_0 = cast(
                    Literal["LOG_UNAVAILABLE"], data
                )
                if componentsschemas_ci_failure_undiagnosed_type_0 != "LOG_UNAVAILABLE":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_0 must match const 'LOG_UNAVAILABLE', got '{componentsschemas_ci_failure_undiagnosed_type_0}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "LOG_TOO_LARGE"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_1 = cast(
                    Literal["LOG_TOO_LARGE"], data
                )
                if componentsschemas_ci_failure_undiagnosed_type_1 != "LOG_TOO_LARGE":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_1 must match const 'LOG_TOO_LARGE', got '{componentsschemas_ci_failure_undiagnosed_type_1}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "LOG_NOT_ADMITTED"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_2 = cast(
                    Literal["LOG_NOT_ADMITTED"], data
                )
                if componentsschemas_ci_failure_undiagnosed_type_2 != "LOG_NOT_ADMITTED":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_2 must match const 'LOG_NOT_ADMITTED', got '{componentsschemas_ci_failure_undiagnosed_type_2}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "DECISION_UNAVAILABLE"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_3 = cast(
                    Literal["DECISION_UNAVAILABLE"], data
                )
                if componentsschemas_ci_failure_undiagnosed_type_3 != "DECISION_UNAVAILABLE":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_3 must match const 'DECISION_UNAVAILABLE', got '{componentsschemas_ci_failure_undiagnosed_type_3}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "SHADOW"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_4 = cast(Literal["SHADOW"], data)
                if componentsschemas_ci_failure_undiagnosed_type_4 != "SHADOW":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_4 must match const 'SHADOW', got '{componentsschemas_ci_failure_undiagnosed_type_4}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNDETERMINED"):
                    raise TypeError()
                componentsschemas_ci_failure_undiagnosed_type_5 = cast(
                    Literal["UNDETERMINED"], data
                )
                if componentsschemas_ci_failure_undiagnosed_type_5 != "UNDETERMINED":
                    raise ValueError(
                        f"/components/schemas/CiFailureUndiagnosed_type_5 must match const 'UNDETERMINED', got '{componentsschemas_ci_failure_undiagnosed_type_5}'"
                    )
                return componentsschemas_ci_failure_undiagnosed_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["DECISION_UNAVAILABLE"]
                | Literal["LOG_NOT_ADMITTED"]
                | Literal["LOG_TOO_LARGE"]
                | Literal["LOG_UNAVAILABLE"]
                | Literal["SHADOW"]
                | Literal["UNDETERMINED"]
                | None
                | Unset,
                data,
            )

        undiagnosed = _parse_undiagnosed(d.pop("undiagnosed", UNSET))

        ci_failure_line = cls(
            attribution=attribution,
            job_name=job_name,
            run_attempt=run_attempt,
            timed_out=timed_out,
            failed_step=failed_step,
            undiagnosed=undiagnosed,
        )

        ci_failure_line.additional_properties = d
        return ci_failure_line

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
