from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.finding_evidence_class_type_0 import FindingEvidenceClassType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.comment_address_evaluation_view import CommentAddressEvaluationView
    from ..models.comment_reaction_view import CommentReactionView
    from ..models.customer_evidence_ref import CustomerEvidenceRef
    from ..models.customer_finding_validation import CustomerFindingValidation
    from ..models.finding_causal_graph_view import FindingCausalGraphView
    from ..models.finding_placement_view import FindingPlacementView
    from ..models.finding_rule_ref_view import FindingRuleRefView
    from ..models.finding_support import FindingSupport
    from ..models.matched_local_finding import MatchedLocalFinding
    from ..models.thread_observation_view import ThreadObservationView


T = TypeVar("T", bound="CustomerFinding")


@_attrs_define
class CustomerFinding:
    """
    Attributes:
        claim (str): What the reviewer states is wrong.
        comment_reactions (list[CommentReactionView]): Emoji reactions stored on the Proofline finding comment. They are
            not a
             finding decision.
        evidence_refs (list[CustomerEvidenceRef]): The references the finding cites, resolved as the pull request
            comment
             resolves them.
        id (UUID): The finding's ID.
        impact (str): The consequence the reviewer states the claim has.
        lifecycle_state (str): The finding's recorded lifecycle state: `NEW`, `UNCHANGED`, `RESOLVED`
             or `REINTRODUCED`.
        risk_domain (str): The risk domain the reviewer assigned to the finding.
        rule_refs (list[FindingRuleRefView]): The bound review rules the reviewer cited for this finding, by key and
             the revisions its assessment showed the reviewer. A finding carried
             forward unchanged keeps the citations of the finding it carries. Empty
             when it cited none.
        severity (str): `SERIOUS` or `WARNING`.
        symbols (list[str]): The code identifiers the reviewer declared in the finding's prose, in
             declaration order, so a reader can set each as code.
        causal_graph (FindingCausalGraphView | None | Unset): The typed causal graph the reviewer supplied for an
            ordering or
             reachability finding. Null when the finding carries none.
        comment_evaluation (CommentAddressEvaluationView | None | Unset): The post-merge judgment of whether the finding
            comment was addressed.
             It is not a finding decision; null when none is recorded.
        evidence_class (FindingEvidenceClassType0 | Literal['EXPERIMENT_BACKED'] | Literal['WORLD_EVIDENCED'] | None |
            Unset): The kind of proof the finding rests on, derived from the typed evidence
             it cites. Null on findings recorded before the class existed.
        finding_fingerprint (None | str | Unset): The retained semantic fingerprint used to correlate findings. It is
             opaque and separate from the occurrence ID and reviewed code digest.
             Absent when no fingerprint is retained; no replacement is derived.
        github_comment_url (None | str | Unset): The inline GitHub comment published for this occurrence of the finding.
             Null when none was published; earlier runs are never used as a fallback.
        latest_validation (CustomerFindingValidation | None | Unset): The latest decision on the finding's series, with
            who made it, where
             and when. Null when no decision is recorded.
        local_findings (list[MatchedLocalFinding] | Unset): Earlier occurrences in the author's local reviews linked by
            exact patch
             identity. These links carry no verdict or finding decision.
        placement (FindingPlacementView | None | Unset): Where this review's comment gate placed the finding, as it
            recorded
             the placement. Null when the review recorded none.
        remediation (None | str | Unset): The reviewer's proposed fix. Null when it proposed none.
        supporting_evidence (FindingSupport | None | Unset): The verdict explanation and evidence of the supported
            hypothesis that
             produced this finding. Null when the finding links no supported
             hypothesis.
        thread_observation (None | ThreadObservationView | Unset): The latest observation of the finding's GitHub thread
            state. It is not
             a finding decision; null when none is recorded.
        validation (None | str | Unset): The latest decision on the finding, the same value `latest_validation`
             carries. Null when no decision is recorded.
    """

    claim: str
    comment_reactions: list[CommentReactionView]
    evidence_refs: list[CustomerEvidenceRef]
    id: UUID
    impact: str
    lifecycle_state: str
    risk_domain: str
    rule_refs: list[FindingRuleRefView]
    severity: str
    symbols: list[str]
    causal_graph: FindingCausalGraphView | None | Unset = UNSET
    comment_evaluation: CommentAddressEvaluationView | None | Unset = UNSET
    evidence_class: (
        FindingEvidenceClassType0
        | Literal["EXPERIMENT_BACKED"]
        | Literal["WORLD_EVIDENCED"]
        | None
        | Unset
    ) = UNSET
    finding_fingerprint: None | str | Unset = UNSET
    github_comment_url: None | str | Unset = UNSET
    latest_validation: CustomerFindingValidation | None | Unset = UNSET
    local_findings: list[MatchedLocalFinding] | Unset = UNSET
    placement: FindingPlacementView | None | Unset = UNSET
    remediation: None | str | Unset = UNSET
    supporting_evidence: FindingSupport | None | Unset = UNSET
    thread_observation: None | ThreadObservationView | Unset = UNSET
    validation: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.comment_address_evaluation_view import (
            CommentAddressEvaluationView,  # noqa: PLC0415
        )
        from ..models.customer_finding_validation import CustomerFindingValidation  # noqa: PLC0415
        from ..models.finding_causal_graph_view import FindingCausalGraphView  # noqa: PLC0415
        from ..models.finding_placement_view import FindingPlacementView  # noqa: PLC0415
        from ..models.finding_support import FindingSupport  # noqa: PLC0415
        from ..models.thread_observation_view import ThreadObservationView  # noqa: PLC0415

        claim = self.claim

        comment_reactions = []
        for comment_reactions_item_data in self.comment_reactions:
            comment_reactions_item = comment_reactions_item_data.to_dict()
            comment_reactions.append(comment_reactions_item)

        evidence_refs = []
        for evidence_refs_item_data in self.evidence_refs:
            evidence_refs_item = evidence_refs_item_data.to_dict()
            evidence_refs.append(evidence_refs_item)

        id = str(self.id)

        impact = self.impact

        lifecycle_state = self.lifecycle_state

        risk_domain = self.risk_domain

        rule_refs = []
        for rule_refs_item_data in self.rule_refs:
            rule_refs_item = rule_refs_item_data.to_dict()
            rule_refs.append(rule_refs_item)

        severity = self.severity

        symbols = self.symbols

        causal_graph: dict[str, Any] | None | Unset
        if isinstance(self.causal_graph, Unset):
            causal_graph = UNSET
        elif isinstance(self.causal_graph, FindingCausalGraphView):
            causal_graph = self.causal_graph.to_dict()
        else:
            causal_graph = self.causal_graph

        comment_evaluation: dict[str, Any] | None | Unset
        if isinstance(self.comment_evaluation, Unset):
            comment_evaluation = UNSET
        elif isinstance(self.comment_evaluation, CommentAddressEvaluationView):
            comment_evaluation = self.comment_evaluation.to_dict()
        else:
            comment_evaluation = self.comment_evaluation

        evidence_class: (
            Literal["EXPERIMENT_BACKED"] | Literal["WORLD_EVIDENCED"] | None | str | Unset
        )
        if isinstance(self.evidence_class, Unset):
            evidence_class = UNSET
        elif isinstance(self.evidence_class, FindingEvidenceClassType0):
            evidence_class = self.evidence_class.value
        else:
            evidence_class = self.evidence_class

        finding_fingerprint: None | str | Unset
        if isinstance(self.finding_fingerprint, Unset):
            finding_fingerprint = UNSET
        else:
            finding_fingerprint = self.finding_fingerprint

        github_comment_url: None | str | Unset
        if isinstance(self.github_comment_url, Unset):
            github_comment_url = UNSET
        else:
            github_comment_url = self.github_comment_url

        latest_validation: dict[str, Any] | None | Unset
        if isinstance(self.latest_validation, Unset):
            latest_validation = UNSET
        elif isinstance(self.latest_validation, CustomerFindingValidation):
            latest_validation = self.latest_validation.to_dict()
        else:
            latest_validation = self.latest_validation

        local_findings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.local_findings, Unset):
            local_findings = []
            for local_findings_item_data in self.local_findings:
                local_findings_item = local_findings_item_data.to_dict()
                local_findings.append(local_findings_item)

        placement: dict[str, Any] | None | Unset
        if isinstance(self.placement, Unset):
            placement = UNSET
        elif isinstance(self.placement, FindingPlacementView):
            placement = self.placement.to_dict()
        else:
            placement = self.placement

        remediation: None | str | Unset
        if isinstance(self.remediation, Unset):
            remediation = UNSET
        else:
            remediation = self.remediation

        supporting_evidence: dict[str, Any] | None | Unset
        if isinstance(self.supporting_evidence, Unset):
            supporting_evidence = UNSET
        elif isinstance(self.supporting_evidence, FindingSupport):
            supporting_evidence = self.supporting_evidence.to_dict()
        else:
            supporting_evidence = self.supporting_evidence

        thread_observation: dict[str, Any] | None | Unset
        if isinstance(self.thread_observation, Unset):
            thread_observation = UNSET
        elif isinstance(self.thread_observation, ThreadObservationView):
            thread_observation = self.thread_observation.to_dict()
        else:
            thread_observation = self.thread_observation

        validation: None | str | Unset
        if isinstance(self.validation, Unset):
            validation = UNSET
        else:
            validation = self.validation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "claim": claim,
                "comment_reactions": comment_reactions,
                "evidence_refs": evidence_refs,
                "id": id,
                "impact": impact,
                "lifecycle_state": lifecycle_state,
                "risk_domain": risk_domain,
                "rule_refs": rule_refs,
                "severity": severity,
                "symbols": symbols,
            }
        )
        if causal_graph is not UNSET:
            field_dict["causal_graph"] = causal_graph
        if comment_evaluation is not UNSET:
            field_dict["comment_evaluation"] = comment_evaluation
        if evidence_class is not UNSET:
            field_dict["evidence_class"] = evidence_class
        if finding_fingerprint is not UNSET:
            field_dict["finding_fingerprint"] = finding_fingerprint
        if github_comment_url is not UNSET:
            field_dict["github_comment_url"] = github_comment_url
        if latest_validation is not UNSET:
            field_dict["latest_validation"] = latest_validation
        if local_findings is not UNSET:
            field_dict["local_findings"] = local_findings
        if placement is not UNSET:
            field_dict["placement"] = placement
        if remediation is not UNSET:
            field_dict["remediation"] = remediation
        if supporting_evidence is not UNSET:
            field_dict["supporting_evidence"] = supporting_evidence
        if thread_observation is not UNSET:
            field_dict["thread_observation"] = thread_observation
        if validation is not UNSET:
            field_dict["validation"] = validation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comment_address_evaluation_view import (
            CommentAddressEvaluationView,  # noqa: PLC0415
        )
        from ..models.comment_reaction_view import CommentReactionView  # noqa: PLC0415
        from ..models.customer_evidence_ref import CustomerEvidenceRef  # noqa: PLC0415
        from ..models.customer_finding_validation import CustomerFindingValidation  # noqa: PLC0415
        from ..models.finding_causal_graph_view import FindingCausalGraphView  # noqa: PLC0415
        from ..models.finding_placement_view import FindingPlacementView  # noqa: PLC0415
        from ..models.finding_rule_ref_view import FindingRuleRefView  # noqa: PLC0415
        from ..models.finding_support import FindingSupport  # noqa: PLC0415
        from ..models.matched_local_finding import MatchedLocalFinding  # noqa: PLC0415
        from ..models.thread_observation_view import ThreadObservationView  # noqa: PLC0415

        d = dict(src_dict)
        claim = d.pop("claim")

        comment_reactions = []
        _comment_reactions = d.pop("comment_reactions")
        for comment_reactions_item_data in _comment_reactions:
            comment_reactions_item = CommentReactionView.from_dict(comment_reactions_item_data)

            comment_reactions.append(comment_reactions_item)

        evidence_refs = []
        _evidence_refs = d.pop("evidence_refs")
        for evidence_refs_item_data in _evidence_refs:
            evidence_refs_item = CustomerEvidenceRef.from_dict(evidence_refs_item_data)

            evidence_refs.append(evidence_refs_item)

        id = UUID(d.pop("id"))

        impact = d.pop("impact")

        lifecycle_state = d.pop("lifecycle_state")

        risk_domain = d.pop("risk_domain")

        rule_refs = []
        _rule_refs = d.pop("rule_refs")
        for rule_refs_item_data in _rule_refs:
            rule_refs_item = FindingRuleRefView.from_dict(rule_refs_item_data)

            rule_refs.append(rule_refs_item)

        severity = d.pop("severity")

        symbols = cast(list[str], d.pop("symbols"))

        def _parse_causal_graph(data: object) -> FindingCausalGraphView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                causal_graph_type_0 = FindingCausalGraphView.from_dict(data)

                return causal_graph_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingCausalGraphView | None | Unset, data)

        causal_graph = _parse_causal_graph(d.pop("causal_graph", UNSET))

        def _parse_comment_evaluation(data: object) -> CommentAddressEvaluationView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                comment_evaluation_type_0 = CommentAddressEvaluationView.from_dict(data)

                return comment_evaluation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CommentAddressEvaluationView | None | Unset, data)

        comment_evaluation = _parse_comment_evaluation(d.pop("comment_evaluation", UNSET))

        def _parse_evidence_class(
            data: object,
        ) -> (
            FindingEvidenceClassType0
            | Literal["EXPERIMENT_BACKED"]
            | Literal["WORLD_EVIDENCED"]
            | None
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_finding_evidence_class_type_0 = FindingEvidenceClassType0(data)

                return componentsschemas_finding_evidence_class_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "WORLD_EVIDENCED"):
                    raise TypeError()
                componentsschemas_finding_evidence_class_type_1 = cast(
                    Literal["WORLD_EVIDENCED"], data
                )
                if componentsschemas_finding_evidence_class_type_1 != "WORLD_EVIDENCED":
                    raise ValueError(
                        f"/components/schemas/FindingEvidenceClass_type_1 must match const 'WORLD_EVIDENCED', got '{componentsschemas_finding_evidence_class_type_1}'"
                    )
                return componentsschemas_finding_evidence_class_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "EXPERIMENT_BACKED"):
                    raise TypeError()
                componentsschemas_finding_evidence_class_type_2 = cast(
                    Literal["EXPERIMENT_BACKED"], data
                )
                if componentsschemas_finding_evidence_class_type_2 != "EXPERIMENT_BACKED":
                    raise ValueError(
                        f"/components/schemas/FindingEvidenceClass_type_2 must match const 'EXPERIMENT_BACKED', got '{componentsschemas_finding_evidence_class_type_2}'"
                    )
                return componentsschemas_finding_evidence_class_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                FindingEvidenceClassType0
                | Literal["EXPERIMENT_BACKED"]
                | Literal["WORLD_EVIDENCED"]
                | None
                | Unset,
                data,
            )

        evidence_class = _parse_evidence_class(d.pop("evidence_class", UNSET))

        def _parse_finding_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        finding_fingerprint = _parse_finding_fingerprint(d.pop("finding_fingerprint", UNSET))

        def _parse_github_comment_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        github_comment_url = _parse_github_comment_url(d.pop("github_comment_url", UNSET))

        def _parse_latest_validation(data: object) -> CustomerFindingValidation | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_validation_type_0 = CustomerFindingValidation.from_dict(data)

                return latest_validation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CustomerFindingValidation | None | Unset, data)

        latest_validation = _parse_latest_validation(d.pop("latest_validation", UNSET))

        _local_findings = d.pop("local_findings", UNSET)
        local_findings: list[MatchedLocalFinding] | Unset = UNSET
        if _local_findings is not UNSET:
            local_findings = []
            for local_findings_item_data in _local_findings:
                local_findings_item = MatchedLocalFinding.from_dict(local_findings_item_data)

                local_findings.append(local_findings_item)

        def _parse_placement(data: object) -> FindingPlacementView | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                placement_type_0 = FindingPlacementView.from_dict(data)

                return placement_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingPlacementView | None | Unset, data)

        placement = _parse_placement(d.pop("placement", UNSET))

        def _parse_remediation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        remediation = _parse_remediation(d.pop("remediation", UNSET))

        def _parse_supporting_evidence(data: object) -> FindingSupport | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                supporting_evidence_type_0 = FindingSupport.from_dict(data)

                return supporting_evidence_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FindingSupport | None | Unset, data)

        supporting_evidence = _parse_supporting_evidence(d.pop("supporting_evidence", UNSET))

        def _parse_thread_observation(data: object) -> None | ThreadObservationView | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                thread_observation_type_0 = ThreadObservationView.from_dict(data)

                return thread_observation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ThreadObservationView | Unset, data)

        thread_observation = _parse_thread_observation(d.pop("thread_observation", UNSET))

        def _parse_validation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        validation = _parse_validation(d.pop("validation", UNSET))

        customer_finding = cls(
            claim=claim,
            comment_reactions=comment_reactions,
            evidence_refs=evidence_refs,
            id=id,
            impact=impact,
            lifecycle_state=lifecycle_state,
            risk_domain=risk_domain,
            rule_refs=rule_refs,
            severity=severity,
            symbols=symbols,
            causal_graph=causal_graph,
            comment_evaluation=comment_evaluation,
            evidence_class=evidence_class,
            finding_fingerprint=finding_fingerprint,
            github_comment_url=github_comment_url,
            latest_validation=latest_validation,
            local_findings=local_findings,
            placement=placement,
            remediation=remediation,
            supporting_evidence=supporting_evidence,
            thread_observation=thread_observation,
            validation=validation,
        )

        customer_finding.additional_properties = d
        return customer_finding

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
