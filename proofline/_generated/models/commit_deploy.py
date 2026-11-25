from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.commit_deploy_rollback import CommitDeployRollback
    from ..models.deploy_coverage_checkpoint import DeployCoverageCheckpoint


T = TypeVar("T", bound="CommitDeploy")


@_attrs_define
class CommitDeploy:
    """One deploy of the commit and where its verification stands.

    Attributes:
        checkpoints (list[DeployCoverageCheckpoint]): The four checks in order, each with its recorded result, if any,
            and
             when a missing one becomes overdue. Empty when no verification of
             the deploy exists.
        environment_id (UUID): The Proofline environment that holds the deploy.
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
            Literal['TELEMETRY_CONNECTION_UNAVAILABLE'] | Literal['TELEMETRY_CREDENTIAL_UNAVAILABLE'] | str]): What the
            checks that leave the deploy unproven name.
        regressed (bool): Whether any check recorded `REGRESSED`, whatever its gaps.
        state (Literal['FAILED'] | Literal['INACTIVE'] | Literal['INCOMPLETE'] | Literal['NOT_YET_DUE'] |
            Literal['SUPERSEDED'] | Literal['UNRECORDED'] | Literal['UNVERIFIED'] | Literal['VERIFIED'] |
            Literal['VERIFIED_UNTIL_SUPERSEDED'] | str): Where one deploy's verification stands. Each deploy has exactly
            one, so
             the counts add up to the population.
        deploy_url (None | str | Unset): The deploy's console page.
        deployment_task (None | str | Unset): The GitHub deployment's task, such as `deploy` or `deploy:web`.
        github_environment (None | str | Unset): The GitHub Environment the deployment named.
        rollback (CommitDeployRollback | None | Unset): Present when the deploy is a rollback: the previous deploy of
            the same
             task ran a commit that a recorded merge into this commit's branch made
             after this commit, as the deploy's console page reads it. Absent for a
             forward deploy and when either merge is unrecorded.
        workflow_run_attempt (int | None | Unset): The attempt of that run that created the deployment addressing the
             deploy; above 1 for a rerun.
        workflow_run_attempts (list[int] | Unset): Each distinct attempt of that run that created one of the deploy's
             deployments, ascending. A retry of a job that failed belongs to the
             deploy it retried, and a re-run of a job that had already landed is a
             deploy of its own. Absent outside Actions and when no recorded
             deployment of the deploy names its attempt.
        workflow_run_id (int | None | Unset): The Actions run that created the deploy's deployments; absent outside
             Actions.
        rolled_back (bool | Unset): Whether the deploy's newest recorded check found its service serving
             an earlier deploy again, as its console page reads it. A later check
             that finds none clears it, while `regressed` keeps an earlier
             regression. Older responses omit it, which reads as false. Default: False.
        github_deployment_ids (list[int] | Unset): The ID of each GitHub deployment the deploy holds, ascending: the
             deployment a pipeline created, or each one an Actions run's jobs
             created. A deployment outside Actions is a deploy of its own, so two
             of one commit, GitHub Environment and task read apart by this ID.
             Every GitHub deploy holds one; a server from before the field existed
             omits it.
        verification_ended (bool | Unset): Whether the deploy's verification ended. A check with no `result`
             then will never be recorded, while a running verification can still
             record one that is overdue; `state` reads `UNRECORDED` for both.
             False without a verification, which `state` reads as `UNVERIFIED`.
             Older responses omit it, which reads as false. Default: False.
        aws_provider (None | str | Unset): The provider of an AWS deploy (`AWS_CODEPIPELINE` or `AWS_AMPLIFY`).
        aws_run_id (None | str | Unset): The `CodePipeline` execution ID or Amplify job ID.
    """

    checkpoints: list[DeployCoverageCheckpoint]
    environment_id: UUID
    gaps: list[
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
        | str
    ]
    regressed: bool
    state: (
        Literal["FAILED"]
        | Literal["INACTIVE"]
        | Literal["INCOMPLETE"]
        | Literal["NOT_YET_DUE"]
        | Literal["SUPERSEDED"]
        | Literal["UNRECORDED"]
        | Literal["UNVERIFIED"]
        | Literal["VERIFIED"]
        | Literal["VERIFIED_UNTIL_SUPERSEDED"]
        | str
    )
    deploy_url: None | str | Unset = UNSET
    deployment_task: None | str | Unset = UNSET
    github_environment: None | str | Unset = UNSET
    rollback: CommitDeployRollback | None | Unset = UNSET
    workflow_run_attempt: int | None | Unset = UNSET
    workflow_run_attempts: list[int] | Unset = UNSET
    workflow_run_id: int | None | Unset = UNSET
    rolled_back: bool | Unset = False
    github_deployment_ids: list[int] | Unset = UNSET
    verification_ended: bool | Unset = False
    aws_provider: None | str | Unset = UNSET
    aws_run_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.commit_deploy_rollback import CommitDeployRollback  # noqa: PLC0415

        checkpoints = []
        for checkpoints_item_data in self.checkpoints:
            checkpoints_item = checkpoints_item_data.to_dict()
            checkpoints.append(checkpoints_item)

        environment_id = str(self.environment_id)

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
                | str
            )
            gaps_item = gaps_item_data
            gaps.append(gaps_item)

        regressed = self.regressed

        state: (
            Literal["FAILED"]
            | Literal["INACTIVE"]
            | Literal["INCOMPLETE"]
            | Literal["NOT_YET_DUE"]
            | Literal["SUPERSEDED"]
            | Literal["UNRECORDED"]
            | Literal["UNVERIFIED"]
            | Literal["VERIFIED"]
            | Literal["VERIFIED_UNTIL_SUPERSEDED"]
            | str
        )
        state = self.state

        deploy_url: None | str | Unset
        if isinstance(self.deploy_url, Unset):
            deploy_url = UNSET
        else:
            deploy_url = self.deploy_url

        deployment_task: None | str | Unset
        if isinstance(self.deployment_task, Unset):
            deployment_task = UNSET
        else:
            deployment_task = self.deployment_task

        github_environment: None | str | Unset
        if isinstance(self.github_environment, Unset):
            github_environment = UNSET
        else:
            github_environment = self.github_environment

        rollback: dict[str, Any] | None | Unset
        if isinstance(self.rollback, Unset):
            rollback = UNSET
        elif isinstance(self.rollback, CommitDeployRollback):
            rollback = self.rollback.to_dict()
        else:
            rollback = self.rollback

        workflow_run_attempt: int | None | Unset
        if isinstance(self.workflow_run_attempt, Unset):
            workflow_run_attempt = UNSET
        else:
            workflow_run_attempt = self.workflow_run_attempt

        workflow_run_attempts: list[int] | Unset = UNSET
        if not isinstance(self.workflow_run_attempts, Unset):
            workflow_run_attempts = self.workflow_run_attempts

        workflow_run_id: int | None | Unset
        if isinstance(self.workflow_run_id, Unset):
            workflow_run_id = UNSET
        else:
            workflow_run_id = self.workflow_run_id

        rolled_back = self.rolled_back

        github_deployment_ids: list[int] | Unset = UNSET
        if not isinstance(self.github_deployment_ids, Unset):
            github_deployment_ids = self.github_deployment_ids

        verification_ended = self.verification_ended

        aws_provider: None | str | Unset
        if isinstance(self.aws_provider, Unset):
            aws_provider = UNSET
        else:
            aws_provider = self.aws_provider

        aws_run_id: None | str | Unset
        if isinstance(self.aws_run_id, Unset):
            aws_run_id = UNSET
        else:
            aws_run_id = self.aws_run_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checkpoints": checkpoints,
                "environment_id": environment_id,
                "gaps": gaps,
                "regressed": regressed,
                "state": state,
            }
        )
        if deploy_url is not UNSET:
            field_dict["deploy_url"] = deploy_url
        if deployment_task is not UNSET:
            field_dict["deployment_task"] = deployment_task
        if github_environment is not UNSET:
            field_dict["github_environment"] = github_environment
        if rollback is not UNSET:
            field_dict["rollback"] = rollback
        if workflow_run_attempt is not UNSET:
            field_dict["workflow_run_attempt"] = workflow_run_attempt
        if workflow_run_attempts is not UNSET:
            field_dict["workflow_run_attempts"] = workflow_run_attempts
        if workflow_run_id is not UNSET:
            field_dict["workflow_run_id"] = workflow_run_id
        if rolled_back is not UNSET:
            field_dict["rolled_back"] = rolled_back
        if github_deployment_ids is not UNSET:
            field_dict["github_deployment_ids"] = github_deployment_ids
        if verification_ended is not UNSET:
            field_dict["verification_ended"] = verification_ended
        if aws_provider is not UNSET:
            field_dict["aws_provider"] = aws_provider
        if aws_run_id is not UNSET:
            field_dict["aws_run_id"] = aws_run_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.commit_deploy_rollback import CommitDeployRollback  # noqa: PLC0415
        from ..models.deploy_coverage_checkpoint import DeployCoverageCheckpoint  # noqa: PLC0415

        d = dict(src_dict)
        checkpoints = []
        _checkpoints = d.pop("checkpoints")
        for checkpoints_item_data in _checkpoints:
            checkpoints_item = DeployCoverageCheckpoint.from_dict(checkpoints_item_data)

            checkpoints.append(checkpoints_item)

        environment_id = UUID(d.pop("environment_id"))

        gaps = []
        _gaps = d.pop("gaps")
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
                | str
            ):
                try:
                    if not (type(data) is str and data == "CHANGE_CHECK_MISSING"):
                        raise TypeError()
                    componentsschemas_deploy_verification_gap_type_0 = cast(
                        Literal["CHANGE_CHECK_MISSING"], data
                    )
                    if componentsschemas_deploy_verification_gap_type_0 != "CHANGE_CHECK_MISSING":
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
                    if not (type(data) is str and data == "AWS_TELEMETRY_CONNECTION_UNAVAILABLE"):
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
                    if componentsschemas_deploy_verification_gap_type_17 != "RUNTIME_TASK_UNMAPPED":
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
                    if componentsschemas_deploy_verification_gap_type_20 != "NO_SIGNALS_CONFIGURED":
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
                    if componentsschemas_deploy_verification_gap_type_25 != "SIGNAL_READ_PARTIAL":
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
                    if componentsschemas_deploy_verification_gap_type_30 != "BASELINE_UNAVAILABLE":
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
                    if componentsschemas_deploy_verification_gap_type_31 != "BELOW_TRAFFIC_FLOOR":
                        raise ValueError(
                            f"/components/schemas/DeployVerificationGap_type_31 must match const 'BELOW_TRAFFIC_FLOOR', got '{componentsschemas_deploy_verification_gap_type_31}'"
                        )
                    return componentsschemas_deploy_verification_gap_type_31
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
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
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                return cast(
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
                    | str,
                    data,
                )

            gaps_item = _parse_gaps_item(gaps_item_data)

            gaps.append(gaps_item)

        regressed = d.pop("regressed")

        def _parse_state(
            data: object,
        ) -> (
            Literal["FAILED"]
            | Literal["INACTIVE"]
            | Literal["INCOMPLETE"]
            | Literal["NOT_YET_DUE"]
            | Literal["SUPERSEDED"]
            | Literal["UNRECORDED"]
            | Literal["UNVERIFIED"]
            | Literal["VERIFIED"]
            | Literal["VERIFIED_UNTIL_SUPERSEDED"]
            | str
        ):
            try:
                if not (type(data) is str and data == "VERIFIED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_0 = cast(Literal["VERIFIED"], data)
                if componentsschemas_deploy_coverage_state_type_0 != "VERIFIED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_0 must match const 'VERIFIED', got '{componentsschemas_deploy_coverage_state_type_0}'"
                    )
                return componentsschemas_deploy_coverage_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "VERIFIED_UNTIL_SUPERSEDED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_1 = cast(
                    Literal["VERIFIED_UNTIL_SUPERSEDED"], data
                )
                if componentsschemas_deploy_coverage_state_type_1 != "VERIFIED_UNTIL_SUPERSEDED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_1 must match const 'VERIFIED_UNTIL_SUPERSEDED', got '{componentsschemas_deploy_coverage_state_type_1}'"
                    )
                return componentsschemas_deploy_coverage_state_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "SUPERSEDED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_2 = cast(Literal["SUPERSEDED"], data)
                if componentsschemas_deploy_coverage_state_type_2 != "SUPERSEDED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_2 must match const 'SUPERSEDED', got '{componentsschemas_deploy_coverage_state_type_2}'"
                    )
                return componentsschemas_deploy_coverage_state_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "INCOMPLETE"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_3 = cast(Literal["INCOMPLETE"], data)
                if componentsschemas_deploy_coverage_state_type_3 != "INCOMPLETE":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_3 must match const 'INCOMPLETE', got '{componentsschemas_deploy_coverage_state_type_3}'"
                    )
                return componentsschemas_deploy_coverage_state_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNRECORDED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_4 = cast(Literal["UNRECORDED"], data)
                if componentsschemas_deploy_coverage_state_type_4 != "UNRECORDED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_4 must match const 'UNRECORDED', got '{componentsschemas_deploy_coverage_state_type_4}'"
                    )
                return componentsschemas_deploy_coverage_state_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NOT_YET_DUE"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_5 = cast(Literal["NOT_YET_DUE"], data)
                if componentsschemas_deploy_coverage_state_type_5 != "NOT_YET_DUE":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_5 must match const 'NOT_YET_DUE', got '{componentsschemas_deploy_coverage_state_type_5}'"
                    )
                return componentsschemas_deploy_coverage_state_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "UNVERIFIED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_6 = cast(Literal["UNVERIFIED"], data)
                if componentsschemas_deploy_coverage_state_type_6 != "UNVERIFIED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_6 must match const 'UNVERIFIED', got '{componentsschemas_deploy_coverage_state_type_6}'"
                    )
                return componentsschemas_deploy_coverage_state_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "FAILED"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_7 = cast(Literal["FAILED"], data)
                if componentsschemas_deploy_coverage_state_type_7 != "FAILED":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_7 must match const 'FAILED', got '{componentsschemas_deploy_coverage_state_type_7}'"
                    )
                return componentsschemas_deploy_coverage_state_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "INACTIVE"):
                    raise TypeError()
                componentsschemas_deploy_coverage_state_type_8 = cast(Literal["INACTIVE"], data)
                if componentsschemas_deploy_coverage_state_type_8 != "INACTIVE":
                    raise ValueError(
                        f"/components/schemas/DeployCoverageState_type_8 must match const 'INACTIVE', got '{componentsschemas_deploy_coverage_state_type_8}'"
                    )
                return componentsschemas_deploy_coverage_state_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                Literal["FAILED"]
                | Literal["INACTIVE"]
                | Literal["INCOMPLETE"]
                | Literal["NOT_YET_DUE"]
                | Literal["SUPERSEDED"]
                | Literal["UNRECORDED"]
                | Literal["UNVERIFIED"]
                | Literal["VERIFIED"]
                | Literal["VERIFIED_UNTIL_SUPERSEDED"]
                | str,
                data,
            )

        state = _parse_state(d.pop("state"))

        def _parse_deploy_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deploy_url = _parse_deploy_url(d.pop("deploy_url", UNSET))

        def _parse_deployment_task(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deployment_task = _parse_deployment_task(d.pop("deployment_task", UNSET))

        def _parse_github_environment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        github_environment = _parse_github_environment(d.pop("github_environment", UNSET))

        def _parse_rollback(data: object) -> CommitDeployRollback | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rollback_type_0 = CommitDeployRollback.from_dict(data)

                return rollback_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CommitDeployRollback | None | Unset, data)

        rollback = _parse_rollback(d.pop("rollback", UNSET))

        def _parse_workflow_run_attempt(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        workflow_run_attempt = _parse_workflow_run_attempt(d.pop("workflow_run_attempt", UNSET))

        workflow_run_attempts = cast(list[int], d.pop("workflow_run_attempts", UNSET))

        def _parse_workflow_run_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        workflow_run_id = _parse_workflow_run_id(d.pop("workflow_run_id", UNSET))

        rolled_back = d.pop("rolled_back", UNSET)

        github_deployment_ids = cast(list[int], d.pop("github_deployment_ids", UNSET))

        verification_ended = d.pop("verification_ended", UNSET)

        def _parse_aws_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        aws_provider = _parse_aws_provider(d.pop("aws_provider", UNSET))

        def _parse_aws_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        aws_run_id = _parse_aws_run_id(d.pop("aws_run_id", UNSET))

        commit_deploy = cls(
            checkpoints=checkpoints,
            environment_id=environment_id,
            gaps=gaps,
            regressed=regressed,
            state=state,
            deploy_url=deploy_url,
            deployment_task=deployment_task,
            github_environment=github_environment,
            rollback=rollback,
            workflow_run_attempt=workflow_run_attempt,
            workflow_run_attempts=workflow_run_attempts,
            workflow_run_id=workflow_run_id,
            rolled_back=rolled_back,
            github_deployment_ids=github_deployment_ids,
            verification_ended=verification_ended,
            aws_provider=aws_provider,
            aws_run_id=aws_run_id,
        )

        commit_deploy.additional_properties = d
        return commit_deploy

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
