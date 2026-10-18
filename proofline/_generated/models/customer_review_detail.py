from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.patch_trigger_source import PatchTriggerSource
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actor_view import ActorView
    from ..models.change_diagram_view import ChangeDiagramView
    from ..models.customer_assessment import CustomerAssessment
    from ..models.customer_code_assessment import CustomerCodeAssessment
    from ..models.deep_review_escalation import DeepReviewEscalation
    from ..models.local_reverification import LocalReverification
    from ..models.open_items_view import OpenItemsView
    from ..models.pull_request_merge_gate import PullRequestMergeGate
    from ..models.refresh_view import RefreshView
    from ..models.related_review import RelatedReview
    from ..models.review_actions import ReviewActions
    from ..models.review_diff_stats import ReviewDiffStats
    from ..models.review_open_items import ReviewOpenItems
    from ..models.subject_view import SubjectView


T = TypeVar("T", bound="CustomerReviewDetail")


@_attrs_define
class CustomerReviewDetail:
    """
    Attributes:
        actions (ReviewActions):
        assessment_count (int): How many environment assessments this review has.
        assessments (list[CustomerAssessment]): The environment assessments this review recorded.
        created_at (datetime.datetime): When the review was created.
        environment_display_names (list[str]): Display names of this review's assessed environments, not current
            repository links.
        finding_count (int): How many findings this review's assessments recorded, across all of them.
        id (UUID): The review's identifier.
        kind (str): `PULL_REQUEST`, `DEPLOYMENT`, `PATCH`, a review of local changes
             sent as a patch, `COMMIT`, a review of pushed commits, or `FILES`,
             complete selected files at one pushed commit.
        public_key (str): The review's stable public address: `rev_` followed by its identifier without hyphens.
        publication (str): Whether the review reached the pull request: `PUBLISHED`, `WITHHELD`,
             `PUBLICATION_REQUESTED` or `PUBLICATION_REFUSED`. A review run from
             Proofline is withheld until somebody publishes it.
        related_reviews (list[RelatedReview]): Every other run for this pull request the caller can see, plus reviews
             joined to this one by supersession or rerun.
        status (str): The review's lifecycle status: `PENDING`, `RUNNING`, `COMPLETED`, `INCOMPLETE`, `FAILED`,
            `SUPERSEDED`, `STOPPED` or `EXCLUDED`.
        stoppable (bool): Whether the stop action applies: the review is `PENDING` or `RUNNING`
             and decides no deployment gate. It says nothing about the caller's
             permission.
        subjects (list[SubjectView]): What this review covers: the revision under review and any companion
             repositories, workflow runs, artifacts or deployments.
        trigger_origin (str): Who asked for this review: `AUTOMATIC`, `COMMAND`, `RERUN`, `MANUAL`,
             or `UNKNOWN` for a trigger key this build does not recognise.
        base_branch_commit_sha (None | str | Unset): The base branch tip GitHub reported when the review was triggered,
             display metadata that differs from `base_commit_sha` when the base
             branch moved after the branch point.
        base_commit_sha (None | str | Unset): The base revision the review compares against; for a pull request, the
             merge base of its head and base branch. Null until pinned, and for a
             first deployment.
        base_commit_url (None | str | Unset): The GitHub page for `base_commit_sha`. Null when that commit or the
             repository is unknown.
        base_ref (None | str | Unset): The pull request's base branch name as last recorded from GitHub, for
             orientation only. Null when no pull request state is recorded.
        change_diagram (ChangeDiagramView | None | Unset): The change-level diagram: the changed call path from the
            pinned code
             index and the relations World declares. Absent when the review
             recorded none.
        check_run_url (None | str | Unset): The GitHub check run Proofline published for this review. Null when
             none was published.
        code_assessment (CustomerCodeAssessment | None | Unset): The code assessment this review recorded, apart from
            its environment
             assessments. Null when the review recorded none. It never completes an
             environment assessment, and no environment count includes its findings.
        compare_url (None | str | Unset): The GitHub comparison of the base and head commits. Null unless both
             are pinned and the repository is known, and for a patch review, whose
             head GitHub does not have.
        completed_at (datetime.datetime | None | Unset): When the review reached a terminal status. Absent while it is
            still pending or running.
        current_head_commit_sha (None | str | Unset): The pull request's head commit as the latest provider projection
            reports it, which can differ from `head_commit_sha`. Set only on a single-review read, and absent for a
            deployment review or a pull request with no projection.
        deep_review_escalation (DeepReviewEscalation | None | Unset): Automatic Deep Review outcome for this exact
            pinned comparison. Absent
             when no sensitive-path evaluation receipt was recorded.
        diff_stats (None | ReviewDiffStats | Unset): Line totals from this run's pinned comparison. Null until recorded,
            or
             when the provider's changed-file list was incomplete.
        head_commit_sha (None | str | Unset): The head commit this review is pinned to. For a patch review, the
             revision ID Proofline derives from its base commit and patch digest,
             which is not a commit. Absent when the review recorded none.
        head_commit_url (None | str | Unset): The exact revision reviewed. A commit URL, never a branch URL: the
             branch moves, the reviewed input does not. Absent for a patch review.
        head_ref (None | str | Unset): The pull request's head branch name as last recorded from GitHub, for
             orientation only. Null when no pull request state is recorded.
        local_reverifications (list[LocalReverification] | Unset): For a patch review requested with
            `verify_finding_ids`, each finding
             it re-verifies against the patch and the outcome. The outcome is
             local: the pull request's finding is unchanged whatever it is. Absent
             otherwise.
        merge_gate (None | PullRequestMergeGate | Unset): The deterministic policy for this exact repository/head, when
            opted in.
             Its captured review owner and GitHub bypass remain separate history.
        open_items (None | OpenItemsView | Unset): What Proofline still has open for the reviewed head, counted from the
             current finding decisions. Absent while the review is `PENDING` or
             `RUNNING`.
        open_items_observation (None | ReviewOpenItems | Unset): Dated PR counts with head, evaluated-scope and bounded
            thread proof.
             Absent when that observation is unavailable; scalar counts remain separate.
        publication_detail (None | str | Unset): Why a publication was refused, or how one failed. Server text.
        pull_request_author_avatar_url (None | str | Unset): Provider-supplied avatar URL. Login-derived `.png` URLs do
            not work for
             GitHub App bot accounts and are not portable across GitHub hosts.
        pull_request_author_github_user_id (int | None | Unset): The author's stable GitHub user id: identity for
            profile lookups,
             never display text. Absent when GitHub named no author.
        pull_request_author_login (None | str | Unset): Provider display metadata for the pull request author, not the
            rerun requester.
        pull_request_author_url (None | str | Unset): The author's profile on the deployment's GitHub host. Absent when
            no author login is known.
        pull_request_number (int | None | Unset): The pull request number. Absent for a deployment or patch review.
        pull_request_state (None | str | Unset): Current provider state of the pull request: `OPEN`, `CLOSED`, or
             `MERGED`. Absent for deployment reviews or a missing projection.
        pull_request_title (None | str | Unset): The pull request's title as provider state last reported it, so it
             names the change rather than only numbering it. Untrusted text:
             renderers must treat it as text, never markup.
        pull_request_url (None | str | Unset): The pull request on GitHub. Absent for a deployment review or when the
            repository is unknown.
        refresh (None | RefreshView | Unset): How this review decided what it reviews after a push or a full-review
             request. Absent for a review that refreshes nothing, and while a
             refresh has not decided yet.
        repository_full_name (None | str | Unset): The repository's `owner/name`. Absent when the review names no
            repository.
        repository_id (None | Unset | UUID): The review's repository. Set only on a single-review read, and absent there
            when the review names no repository.
        repository_name (None | str | Unset): The repository's name within its owner. Absent when the review names no
            repository.
        repository_url (None | str | Unset): The repository on GitHub. Absent when the deployment's web base
             cannot be joined with the stored name.
        requested_by (ActorView | None | Unset): Who asked for this review, for a review a person requested. Null on
             automatic reviews and on reviews recorded before requesters were.
        review_comment_url (None | str | Unset): The pull request review Proofline submitted for this review. Null when
             it submitted none.
        review_retracted_at (datetime.datetime | None | Unset): When a submitted pull request review was marked
            retracted, a marker
             only older versions set. Null otherwise.
        run_number (int | None | Unset): One-based, append-only ordinal within one repository pull request.
        stopped_at (datetime.datetime | None | Unset): When the review was stopped. Null unless it was stopped.
        stopped_by (ActorView | None | Unset): Who stopped this review, for a `STOPPED` review whose stop recorded its
             actor. Null otherwise.
        stopped_from (None | str | Unset): Where the review was stopped: `PROOFLINE` or `PULL_REQUEST`. Null unless
             the stop recorded it.
        superseded_by_review_id (None | Unset | UUID): The newer review that superseded this one. Null when none did or
            the
             caller cannot see it.
        trigger_source (None | PatchTriggerSource | Unset): The git hook that asked for this patch review:
            `HOOK_PRE_COMMIT` or
             `HOOK_PRE_PUSH`. Null for any other review, and for a patch review
             requested without naming a hook.
    """

    actions: ReviewActions
    assessment_count: int
    assessments: list[CustomerAssessment]
    created_at: datetime.datetime
    environment_display_names: list[str]
    finding_count: int
    id: UUID
    kind: str
    public_key: str
    publication: str
    related_reviews: list[RelatedReview]
    status: str
    stoppable: bool
    subjects: list[SubjectView]
    trigger_origin: str
    base_branch_commit_sha: None | str | Unset = UNSET
    base_commit_sha: None | str | Unset = UNSET
    base_commit_url: None | str | Unset = UNSET
    base_ref: None | str | Unset = UNSET
    change_diagram: ChangeDiagramView | None | Unset = UNSET
    check_run_url: None | str | Unset = UNSET
    code_assessment: CustomerCodeAssessment | None | Unset = UNSET
    compare_url: None | str | Unset = UNSET
    completed_at: datetime.datetime | None | Unset = UNSET
    current_head_commit_sha: None | str | Unset = UNSET
    deep_review_escalation: DeepReviewEscalation | None | Unset = UNSET
    diff_stats: None | ReviewDiffStats | Unset = UNSET
    head_commit_sha: None | str | Unset = UNSET
    head_commit_url: None | str | Unset = UNSET
    head_ref: None | str | Unset = UNSET
    local_reverifications: list[LocalReverification] | Unset = UNSET
    merge_gate: None | PullRequestMergeGate | Unset = UNSET
    open_items: None | OpenItemsView | Unset = UNSET
    open_items_observation: None | ReviewOpenItems | Unset = UNSET
    publication_detail: None | str | Unset = UNSET
    pull_request_author_avatar_url: None | str | Unset = UNSET
    pull_request_author_github_user_id: int | None | Unset = UNSET
    pull_request_author_login: None | str | Unset = UNSET
    pull_request_author_url: None | str | Unset = UNSET
    pull_request_number: int | None | Unset = UNSET
    pull_request_state: None | str | Unset = UNSET
    pull_request_title: None | str | Unset = UNSET
    pull_request_url: None | str | Unset = UNSET
    refresh: None | RefreshView | Unset = UNSET
    repository_full_name: None | str | Unset = UNSET
    repository_id: None | Unset | UUID = UNSET
    repository_name: None | str | Unset = UNSET
    repository_url: None | str | Unset = UNSET
    requested_by: ActorView | None | Unset = UNSET
    review_comment_url: None | str | Unset = UNSET
    review_retracted_at: datetime.datetime | None | Unset = UNSET
    run_number: int | None | Unset = UNSET
    stopped_at: datetime.datetime | None | Unset = UNSET
    stopped_by: ActorView | None | Unset = UNSET
    stopped_from: None | str | Unset = UNSET
    superseded_by_review_id: None | Unset | UUID = UNSET
    trigger_source: None | PatchTriggerSource | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actor_view import ActorView  # noqa: PLC0415
        from ..models.change_diagram_view import ChangeDiagramView  # noqa: PLC0415
        from ..models.customer_code_assessment import CustomerCodeAssessment  # noqa: PLC0415
        from ..models.deep_review_escalation import DeepReviewEscalation  # noqa: PLC0415
        from ..models.open_items_view import OpenItemsView  # noqa: PLC0415
        from ..models.pull_request_merge_gate import PullRequestMergeGate  # noqa: PLC0415
        from ..models.refresh_view import RefreshView  # noqa: PLC0415
        from ..models.review_diff_stats import ReviewDiffStats  # noqa: PLC0415
        from ..models.review_open_items import ReviewOpenItems  # noqa: PLC0415

        actions = self.actions.to_dict()

        assessment_count = self.assessment_count

        assessments = []
        for assessments_item_data in self.assessments:
            assessments_item = assessments_item_data.to_dict()
            assessments.append(assessments_item)

        created_at = self.created_at.isoformat()

        environment_display_names = self.environment_display_names

        finding_count = self.finding_count

        id = str(self.id)

        kind = self.kind

        public_key = self.public_key

        publication = self.publication

        related_reviews = []
        for related_reviews_item_data in self.related_reviews:
            related_reviews_item = related_reviews_item_data.to_dict()
            related_reviews.append(related_reviews_item)

        status = self.status

        stoppable = self.stoppable

        subjects = []
        for subjects_item_data in self.subjects:
            subjects_item = subjects_item_data.to_dict()
            subjects.append(subjects_item)

        trigger_origin = self.trigger_origin

        base_branch_commit_sha: None | str | Unset
        if isinstance(self.base_branch_commit_sha, Unset):
            base_branch_commit_sha = UNSET
        else:
            base_branch_commit_sha = self.base_branch_commit_sha

        base_commit_sha: None | str | Unset
        if isinstance(self.base_commit_sha, Unset):
            base_commit_sha = UNSET
        else:
            base_commit_sha = self.base_commit_sha

        base_commit_url: None | str | Unset
        if isinstance(self.base_commit_url, Unset):
            base_commit_url = UNSET
        else:
            base_commit_url = self.base_commit_url

        base_ref: None | str | Unset
        if isinstance(self.base_ref, Unset):
            base_ref = UNSET
        else:
            base_ref = self.base_ref

        change_diagram: dict[str, Any] | None | Unset
        if isinstance(self.change_diagram, Unset):
            change_diagram = UNSET
        elif isinstance(self.change_diagram, ChangeDiagramView):
            change_diagram = self.change_diagram.to_dict()
        else:
            change_diagram = self.change_diagram

        check_run_url: None | str | Unset
        if isinstance(self.check_run_url, Unset):
            check_run_url = UNSET
        else:
            check_run_url = self.check_run_url

        code_assessment: dict[str, Any] | None | Unset
        if isinstance(self.code_assessment, Unset):
            code_assessment = UNSET
        elif isinstance(self.code_assessment, CustomerCodeAssessment):
            code_assessment = self.code_assessment.to_dict()
        else:
            code_assessment = self.code_assessment

        compare_url: None | str | Unset
        if isinstance(self.compare_url, Unset):
            compare_url = UNSET
        else:
            compare_url = self.compare_url

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        current_head_commit_sha: None | str | Unset
        if isinstance(self.current_head_commit_sha, Unset):
            current_head_commit_sha = UNSET
        else:
            current_head_commit_sha = self.current_head_commit_sha

        deep_review_escalation: dict[str, Any] | None | Unset
        if isinstance(self.deep_review_escalation, Unset):
            deep_review_escalation = UNSET
        elif isinstance(self.deep_review_escalation, DeepReviewEscalation):
            deep_review_escalation = self.deep_review_escalation.to_dict()
        else:
            deep_review_escalation = self.deep_review_escalation

        diff_stats: dict[str, Any] | None | Unset
        if isinstance(self.diff_stats, Unset):
            diff_stats = UNSET
        elif isinstance(self.diff_stats, ReviewDiffStats):
            diff_stats = self.diff_stats.to_dict()
        else:
            diff_stats = self.diff_stats

        head_commit_sha: None | str | Unset
        if isinstance(self.head_commit_sha, Unset):
            head_commit_sha = UNSET
        else:
            head_commit_sha = self.head_commit_sha

        head_commit_url: None | str | Unset
        if isinstance(self.head_commit_url, Unset):
            head_commit_url = UNSET
        else:
            head_commit_url = self.head_commit_url

        head_ref: None | str | Unset
        if isinstance(self.head_ref, Unset):
            head_ref = UNSET
        else:
            head_ref = self.head_ref

        local_reverifications: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.local_reverifications, Unset):
            local_reverifications = []
            for local_reverifications_item_data in self.local_reverifications:
                local_reverifications_item = local_reverifications_item_data.to_dict()
                local_reverifications.append(local_reverifications_item)

        merge_gate: dict[str, Any] | None | Unset
        if isinstance(self.merge_gate, Unset):
            merge_gate = UNSET
        elif isinstance(self.merge_gate, PullRequestMergeGate):
            merge_gate = self.merge_gate.to_dict()
        else:
            merge_gate = self.merge_gate

        open_items: dict[str, Any] | None | Unset
        if isinstance(self.open_items, Unset):
            open_items = UNSET
        elif isinstance(self.open_items, OpenItemsView):
            open_items = self.open_items.to_dict()
        else:
            open_items = self.open_items

        open_items_observation: dict[str, Any] | None | Unset
        if isinstance(self.open_items_observation, Unset):
            open_items_observation = UNSET
        elif isinstance(self.open_items_observation, ReviewOpenItems):
            open_items_observation = self.open_items_observation.to_dict()
        else:
            open_items_observation = self.open_items_observation

        publication_detail: None | str | Unset
        if isinstance(self.publication_detail, Unset):
            publication_detail = UNSET
        else:
            publication_detail = self.publication_detail

        pull_request_author_avatar_url: None | str | Unset
        if isinstance(self.pull_request_author_avatar_url, Unset):
            pull_request_author_avatar_url = UNSET
        else:
            pull_request_author_avatar_url = self.pull_request_author_avatar_url

        pull_request_author_github_user_id: int | None | Unset
        if isinstance(self.pull_request_author_github_user_id, Unset):
            pull_request_author_github_user_id = UNSET
        else:
            pull_request_author_github_user_id = self.pull_request_author_github_user_id

        pull_request_author_login: None | str | Unset
        if isinstance(self.pull_request_author_login, Unset):
            pull_request_author_login = UNSET
        else:
            pull_request_author_login = self.pull_request_author_login

        pull_request_author_url: None | str | Unset
        if isinstance(self.pull_request_author_url, Unset):
            pull_request_author_url = UNSET
        else:
            pull_request_author_url = self.pull_request_author_url

        pull_request_number: int | None | Unset
        if isinstance(self.pull_request_number, Unset):
            pull_request_number = UNSET
        else:
            pull_request_number = self.pull_request_number

        pull_request_state: None | str | Unset
        if isinstance(self.pull_request_state, Unset):
            pull_request_state = UNSET
        else:
            pull_request_state = self.pull_request_state

        pull_request_title: None | str | Unset
        if isinstance(self.pull_request_title, Unset):
            pull_request_title = UNSET
        else:
            pull_request_title = self.pull_request_title

        pull_request_url: None | str | Unset
        if isinstance(self.pull_request_url, Unset):
            pull_request_url = UNSET
        else:
            pull_request_url = self.pull_request_url

        refresh: dict[str, Any] | None | Unset
        if isinstance(self.refresh, Unset):
            refresh = UNSET
        elif isinstance(self.refresh, RefreshView):
            refresh = self.refresh.to_dict()
        else:
            refresh = self.refresh

        repository_full_name: None | str | Unset
        if isinstance(self.repository_full_name, Unset):
            repository_full_name = UNSET
        else:
            repository_full_name = self.repository_full_name

        repository_id: None | str | Unset
        if isinstance(self.repository_id, Unset):
            repository_id = UNSET
        elif isinstance(self.repository_id, UUID):
            repository_id = str(self.repository_id)
        else:
            repository_id = self.repository_id

        repository_name: None | str | Unset
        if isinstance(self.repository_name, Unset):
            repository_name = UNSET
        else:
            repository_name = self.repository_name

        repository_url: None | str | Unset
        if isinstance(self.repository_url, Unset):
            repository_url = UNSET
        else:
            repository_url = self.repository_url

        requested_by: dict[str, Any] | None | Unset
        if isinstance(self.requested_by, Unset):
            requested_by = UNSET
        elif isinstance(self.requested_by, ActorView):
            requested_by = self.requested_by.to_dict()
        else:
            requested_by = self.requested_by

        review_comment_url: None | str | Unset
        if isinstance(self.review_comment_url, Unset):
            review_comment_url = UNSET
        else:
            review_comment_url = self.review_comment_url

        review_retracted_at: None | str | Unset
        if isinstance(self.review_retracted_at, Unset):
            review_retracted_at = UNSET
        elif isinstance(self.review_retracted_at, datetime.datetime):
            review_retracted_at = self.review_retracted_at.isoformat()
        else:
            review_retracted_at = self.review_retracted_at

        run_number: int | None | Unset
        if isinstance(self.run_number, Unset):
            run_number = UNSET
        else:
            run_number = self.run_number

        stopped_at: None | str | Unset
        if isinstance(self.stopped_at, Unset):
            stopped_at = UNSET
        elif isinstance(self.stopped_at, datetime.datetime):
            stopped_at = self.stopped_at.isoformat()
        else:
            stopped_at = self.stopped_at

        stopped_by: dict[str, Any] | None | Unset
        if isinstance(self.stopped_by, Unset):
            stopped_by = UNSET
        elif isinstance(self.stopped_by, ActorView):
            stopped_by = self.stopped_by.to_dict()
        else:
            stopped_by = self.stopped_by

        stopped_from: None | str | Unset
        if isinstance(self.stopped_from, Unset):
            stopped_from = UNSET
        else:
            stopped_from = self.stopped_from

        superseded_by_review_id: None | str | Unset
        if isinstance(self.superseded_by_review_id, Unset):
            superseded_by_review_id = UNSET
        elif isinstance(self.superseded_by_review_id, UUID):
            superseded_by_review_id = str(self.superseded_by_review_id)
        else:
            superseded_by_review_id = self.superseded_by_review_id

        trigger_source: None | str | Unset
        if isinstance(self.trigger_source, Unset):
            trigger_source = UNSET
        elif isinstance(self.trigger_source, PatchTriggerSource):
            trigger_source = self.trigger_source.value
        else:
            trigger_source = self.trigger_source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actions": actions,
                "assessment_count": assessment_count,
                "assessments": assessments,
                "created_at": created_at,
                "environment_display_names": environment_display_names,
                "finding_count": finding_count,
                "id": id,
                "kind": kind,
                "public_key": public_key,
                "publication": publication,
                "related_reviews": related_reviews,
                "status": status,
                "stoppable": stoppable,
                "subjects": subjects,
                "trigger_origin": trigger_origin,
            }
        )
        if base_branch_commit_sha is not UNSET:
            field_dict["base_branch_commit_sha"] = base_branch_commit_sha
        if base_commit_sha is not UNSET:
            field_dict["base_commit_sha"] = base_commit_sha
        if base_commit_url is not UNSET:
            field_dict["base_commit_url"] = base_commit_url
        if base_ref is not UNSET:
            field_dict["base_ref"] = base_ref
        if change_diagram is not UNSET:
            field_dict["change_diagram"] = change_diagram
        if check_run_url is not UNSET:
            field_dict["check_run_url"] = check_run_url
        if code_assessment is not UNSET:
            field_dict["code_assessment"] = code_assessment
        if compare_url is not UNSET:
            field_dict["compare_url"] = compare_url
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if current_head_commit_sha is not UNSET:
            field_dict["current_head_commit_sha"] = current_head_commit_sha
        if deep_review_escalation is not UNSET:
            field_dict["deep_review_escalation"] = deep_review_escalation
        if diff_stats is not UNSET:
            field_dict["diff_stats"] = diff_stats
        if head_commit_sha is not UNSET:
            field_dict["head_commit_sha"] = head_commit_sha
        if head_commit_url is not UNSET:
            field_dict["head_commit_url"] = head_commit_url
        if head_ref is not UNSET:
            field_dict["head_ref"] = head_ref
        if local_reverifications is not UNSET:
            field_dict["local_reverifications"] = local_reverifications
        if merge_gate is not UNSET:
            field_dict["merge_gate"] = merge_gate
        if open_items is not UNSET:
            field_dict["open_items"] = open_items
        if open_items_observation is not UNSET:
            field_dict["open_items_observation"] = open_items_observation
        if publication_detail is not UNSET:
            field_dict["publication_detail"] = publication_detail
        if pull_request_author_avatar_url is not UNSET:
            field_dict["pull_request_author_avatar_url"] = pull_request_author_avatar_url
        if pull_request_author_github_user_id is not UNSET:
            field_dict["pull_request_author_github_user_id"] = pull_request_author_github_user_id
        if pull_request_author_login is not UNSET:
            field_dict["pull_request_author_login"] = pull_request_author_login
        if pull_request_author_url is not UNSET:
            field_dict["pull_request_author_url"] = pull_request_author_url
        if pull_request_number is not UNSET:
            field_dict["pull_request_number"] = pull_request_number
        if pull_request_state is not UNSET:
            field_dict["pull_request_state"] = pull_request_state
        if pull_request_title is not UNSET:
            field_dict["pull_request_title"] = pull_request_title
        if pull_request_url is not UNSET:
            field_dict["pull_request_url"] = pull_request_url
        if refresh is not UNSET:
            field_dict["refresh"] = refresh
        if repository_full_name is not UNSET:
            field_dict["repository_full_name"] = repository_full_name
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name
        if repository_url is not UNSET:
            field_dict["repository_url"] = repository_url
        if requested_by is not UNSET:
            field_dict["requested_by"] = requested_by
        if review_comment_url is not UNSET:
            field_dict["review_comment_url"] = review_comment_url
        if review_retracted_at is not UNSET:
            field_dict["review_retracted_at"] = review_retracted_at
        if run_number is not UNSET:
            field_dict["run_number"] = run_number
        if stopped_at is not UNSET:
            field_dict["stopped_at"] = stopped_at
        if stopped_by is not UNSET:
            field_dict["stopped_by"] = stopped_by
        if stopped_from is not UNSET:
            field_dict["stopped_from"] = stopped_from
        if superseded_by_review_id is not UNSET:
            field_dict["superseded_by_review_id"] = superseded_by_review_id
        if trigger_source is not UNSET:
            field_dict["trigger_source"] = trigger_source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actor_view import ActorView  # noqa: PLC0415
        from ..models.change_diagram_view import ChangeDiagramView  # noqa: PLC0415
        from ..models.customer_assessment import CustomerAssessment  # noqa: PLC0415
        from ..models.customer_code_assessment import CustomerCodeAssessment  # noqa: PLC0415
        from ..models.deep_review_escalation import DeepReviewEscalation  # noqa: PLC0415
        from ..models.local_reverification import LocalReverification  # noqa: PLC0415
        from ..models.open_items_view import OpenItemsView  # noqa: PLC0415
        from ..models.pull_request_merge_gate import PullRequestMergeGate  # noqa: PLC0415
        from ..models.refresh_view import RefreshView  # noqa: PLC0415
        from ..models.related_review import RelatedReview  # noqa: PLC0415
        from ..models.review_actions import ReviewActions  # noqa: PLC0415
        from ..models.review_diff_stats import ReviewDiffStats  # noqa: PLC0415
        from ..models.review_open_items import ReviewOpenItems  # noqa: PLC0415
        from ..models.subject_view import SubjectView  # noqa: PLC0415

        d = dict(src_dict)
        actions = ReviewActions.from_dict(d.pop("actions"))

        assessment_count = d.pop("assessment_count")

        assessments = []
        _assessments = d.pop("assessments")
        for assessments_item_data in _assessments:
            assessments_item = CustomerAssessment.from_dict(assessments_item_data)

            assessments.append(assessments_item)

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        environment_display_names = cast(list[str], d.pop("environment_display_names"))

        finding_count = d.pop("finding_count")

        id = UUID(d.pop("id"))

        kind = d.pop("kind")

        public_key = d.pop("public_key")

        publication = d.pop("publication")

        related_reviews = []
        _related_reviews = d.pop("related_reviews")
        for related_reviews_item_data in _related_reviews:
            related_reviews_item = RelatedReview.from_dict(related_reviews_item_data)

            related_reviews.append(related_reviews_item)

        status = d.pop("status")

        stoppable = d.pop("stoppable")

        subjects = []
        _subjects = d.pop("subjects")
        for subjects_item_data in _subjects:
            subjects_item = SubjectView.from_dict(subjects_item_data)

            subjects.append(subjects_item)

        trigger_origin = d.pop("trigger_origin")

        def _parse_base_branch_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_branch_commit_sha = _parse_base_branch_commit_sha(
            d.pop("base_branch_commit_sha", UNSET)
        )

        def _parse_base_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_commit_sha = _parse_base_commit_sha(d.pop("base_commit_sha", UNSET))

        def _parse_base_commit_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_commit_url = _parse_base_commit_url(d.pop("base_commit_url", UNSET))

        def _parse_base_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_ref = _parse_base_ref(d.pop("base_ref", UNSET))

        def _parse_change_diagram(data: object) -> ChangeDiagramView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                change_diagram_type_0 = ChangeDiagramView.from_dict(data)

                return change_diagram_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChangeDiagramView | None | Unset, data)

        change_diagram = _parse_change_diagram(d.pop("change_diagram", UNSET))

        def _parse_check_run_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        check_run_url = _parse_check_run_url(d.pop("check_run_url", UNSET))

        def _parse_code_assessment(data: object) -> CustomerCodeAssessment | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                code_assessment_type_0 = CustomerCodeAssessment.from_dict(data)

                return code_assessment_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerCodeAssessment | None | Unset, data)

        code_assessment = _parse_code_assessment(d.pop("code_assessment", UNSET))

        def _parse_compare_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        compare_url = _parse_compare_url(d.pop("compare_url", UNSET))

        def _parse_completed_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = datetime.datetime.fromisoformat(data)

                return completed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_current_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        current_head_commit_sha = _parse_current_head_commit_sha(
            d.pop("current_head_commit_sha", UNSET)
        )

        def _parse_deep_review_escalation(data: object) -> DeepReviewEscalation | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                deep_review_escalation_type_0 = DeepReviewEscalation.from_dict(data)

                return deep_review_escalation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DeepReviewEscalation | None | Unset, data)

        deep_review_escalation = _parse_deep_review_escalation(
            d.pop("deep_review_escalation", UNSET)
        )

        def _parse_diff_stats(data: object) -> None | ReviewDiffStats | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                diff_stats_type_0 = ReviewDiffStats.from_dict(data)

                return diff_stats_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReviewDiffStats | Unset, data)

        diff_stats = _parse_diff_stats(d.pop("diff_stats", UNSET))

        def _parse_head_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_sha = _parse_head_commit_sha(d.pop("head_commit_sha", UNSET))

        def _parse_head_commit_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_commit_url = _parse_head_commit_url(d.pop("head_commit_url", UNSET))

        def _parse_head_ref(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        head_ref = _parse_head_ref(d.pop("head_ref", UNSET))

        _local_reverifications = d.pop("local_reverifications", UNSET)
        local_reverifications: list[LocalReverification] | Unset = UNSET
        if _local_reverifications is not UNSET:
            local_reverifications = []
            for local_reverifications_item_data in _local_reverifications:
                local_reverifications_item = LocalReverification.from_dict(
                    local_reverifications_item_data
                )

                local_reverifications.append(local_reverifications_item)

        def _parse_merge_gate(data: object) -> None | PullRequestMergeGate | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                merge_gate_type_0 = PullRequestMergeGate.from_dict(data)

                return merge_gate_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PullRequestMergeGate | Unset, data)

        merge_gate = _parse_merge_gate(d.pop("merge_gate", UNSET))

        def _parse_open_items(data: object) -> None | OpenItemsView | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                open_items_type_0 = OpenItemsView.from_dict(data)

                return open_items_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenItemsView | Unset, data)

        open_items = _parse_open_items(d.pop("open_items", UNSET))

        def _parse_open_items_observation(data: object) -> None | ReviewOpenItems | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                open_items_observation_type_0 = ReviewOpenItems.from_dict(data)

                return open_items_observation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReviewOpenItems | Unset, data)

        open_items_observation = _parse_open_items_observation(
            d.pop("open_items_observation", UNSET)
        )

        def _parse_publication_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        publication_detail = _parse_publication_detail(d.pop("publication_detail", UNSET))

        def _parse_pull_request_author_avatar_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_avatar_url = _parse_pull_request_author_avatar_url(
            d.pop("pull_request_author_avatar_url", UNSET)
        )

        def _parse_pull_request_author_github_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_author_github_user_id = _parse_pull_request_author_github_user_id(
            d.pop("pull_request_author_github_user_id", UNSET)
        )

        def _parse_pull_request_author_login(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_login = _parse_pull_request_author_login(
            d.pop("pull_request_author_login", UNSET)
        )

        def _parse_pull_request_author_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_author_url = _parse_pull_request_author_url(
            d.pop("pull_request_author_url", UNSET)
        )

        def _parse_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_number = _parse_pull_request_number(d.pop("pull_request_number", UNSET))

        def _parse_pull_request_state(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_state = _parse_pull_request_state(d.pop("pull_request_state", UNSET))

        def _parse_pull_request_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_title = _parse_pull_request_title(d.pop("pull_request_title", UNSET))

        def _parse_pull_request_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_url = _parse_pull_request_url(d.pop("pull_request_url", UNSET))

        def _parse_refresh(data: object) -> None | RefreshView | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                refresh_type_0 = RefreshView.from_dict(data)

                return refresh_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RefreshView | Unset, data)

        refresh = _parse_refresh(d.pop("refresh", UNSET))

        def _parse_repository_full_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_full_name = _parse_repository_full_name(d.pop("repository_full_name", UNSET))

        def _parse_repository_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                repository_id_type_0 = UUID(data)

                return repository_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        repository_id = _parse_repository_id(d.pop("repository_id", UNSET))

        def _parse_repository_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_name = _parse_repository_name(d.pop("repository_name", UNSET))

        def _parse_repository_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_url = _parse_repository_url(d.pop("repository_url", UNSET))

        def _parse_requested_by(data: object) -> ActorView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                requested_by_type_0 = ActorView.from_dict(data)

                return requested_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActorView | None | Unset, data)

        requested_by = _parse_requested_by(d.pop("requested_by", UNSET))

        def _parse_review_comment_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        review_comment_url = _parse_review_comment_url(d.pop("review_comment_url", UNSET))

        def _parse_review_retracted_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                review_retracted_at_type_0 = datetime.datetime.fromisoformat(data)

                return review_retracted_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        review_retracted_at = _parse_review_retracted_at(d.pop("review_retracted_at", UNSET))

        def _parse_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        run_number = _parse_run_number(d.pop("run_number", UNSET))

        def _parse_stopped_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                stopped_at_type_0 = datetime.datetime.fromisoformat(data)

                return stopped_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        stopped_at = _parse_stopped_at(d.pop("stopped_at", UNSET))

        def _parse_stopped_by(data: object) -> ActorView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                stopped_by_type_0 = ActorView.from_dict(data)

                return stopped_by_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActorView | None | Unset, data)

        stopped_by = _parse_stopped_by(d.pop("stopped_by", UNSET))

        def _parse_stopped_from(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stopped_from = _parse_stopped_from(d.pop("stopped_from", UNSET))

        def _parse_superseded_by_review_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                superseded_by_review_id_type_0 = UUID(data)

                return superseded_by_review_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        superseded_by_review_id = _parse_superseded_by_review_id(
            d.pop("superseded_by_review_id", UNSET)
        )

        def _parse_trigger_source(data: object) -> None | PatchTriggerSource | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trigger_source_type_0 = PatchTriggerSource(data)

                return trigger_source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PatchTriggerSource | Unset, data)

        trigger_source = _parse_trigger_source(d.pop("trigger_source", UNSET))

        customer_review_detail = cls(
            actions=actions,
            assessment_count=assessment_count,
            assessments=assessments,
            created_at=created_at,
            environment_display_names=environment_display_names,
            finding_count=finding_count,
            id=id,
            kind=kind,
            public_key=public_key,
            publication=publication,
            related_reviews=related_reviews,
            status=status,
            stoppable=stoppable,
            subjects=subjects,
            trigger_origin=trigger_origin,
            base_branch_commit_sha=base_branch_commit_sha,
            base_commit_sha=base_commit_sha,
            base_commit_url=base_commit_url,
            base_ref=base_ref,
            change_diagram=change_diagram,
            check_run_url=check_run_url,
            code_assessment=code_assessment,
            compare_url=compare_url,
            completed_at=completed_at,
            current_head_commit_sha=current_head_commit_sha,
            deep_review_escalation=deep_review_escalation,
            diff_stats=diff_stats,
            head_commit_sha=head_commit_sha,
            head_commit_url=head_commit_url,
            head_ref=head_ref,
            local_reverifications=local_reverifications,
            merge_gate=merge_gate,
            open_items=open_items,
            open_items_observation=open_items_observation,
            publication_detail=publication_detail,
            pull_request_author_avatar_url=pull_request_author_avatar_url,
            pull_request_author_github_user_id=pull_request_author_github_user_id,
            pull_request_author_login=pull_request_author_login,
            pull_request_author_url=pull_request_author_url,
            pull_request_number=pull_request_number,
            pull_request_state=pull_request_state,
            pull_request_title=pull_request_title,
            pull_request_url=pull_request_url,
            refresh=refresh,
            repository_full_name=repository_full_name,
            repository_id=repository_id,
            repository_name=repository_name,
            repository_url=repository_url,
            requested_by=requested_by,
            review_comment_url=review_comment_url,
            review_retracted_at=review_retracted_at,
            run_number=run_number,
            stopped_at=stopped_at,
            stopped_by=stopped_by,
            stopped_from=stopped_from,
            superseded_by_review_id=superseded_by_review_id,
            trigger_source=trigger_source,
        )

        customer_review_detail.additional_properties = d
        return customer_review_detail

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
