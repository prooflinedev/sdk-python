from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.prose_outcome_type_0 import ProseOutcomeType0
from ..models.summary_route import SummaryRoute
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_fact import FileFact
    from ..models.prose import Prose


T = TypeVar("T", bound="ChangeSummary")


@_attrs_define
class ChangeSummary:
    """What a review recorded about its change.

    Attributes:
        files (list[FileFact]): The changed files the review read, by path, with the depth it read
             them at. Empty when the review recorded no change digest. Files the
             review's filters kept from review are listed apart, with their reason.
        head_sha (str): The reviewed head commit.
        prose_outcome (Literal['MALFORMED'] | Literal['MODEL_UNAVAILABLE'] | Literal['NO_CHANGE_DIGEST'] |
            Literal['NOT_REQUESTED'] | Literal['REJECTED'] | Literal['UNGROUNDED'] | ProseOutcomeType0): Why the summary
            carries prose or does not.
        base_sha (None | str | Unset): The compared base commit. Null when the review pinned none.
        prose (None | Prose | Unset): Model-written prose. Present only when `prose_outcome` is `PUBLISHED`.
             It is untrusted text: render it inert.
        route (None | SummaryRoute | Unset): The route the summary applied. Null when the review recorded no change
             digest, so no route was asked.
    """

    files: list[FileFact]
    head_sha: str
    prose_outcome: (
        Literal["MALFORMED"]
        | Literal["MODEL_UNAVAILABLE"]
        | Literal["NO_CHANGE_DIGEST"]
        | Literal["NOT_REQUESTED"]
        | Literal["REJECTED"]
        | Literal["UNGROUNDED"]
        | ProseOutcomeType0
    )
    base_sha: None | str | Unset = UNSET
    prose: None | Prose | Unset = UNSET
    route: None | SummaryRoute | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prose import Prose  # noqa: PLC0415

        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_dict()
            files.append(files_item)

        head_sha = self.head_sha

        prose_outcome: (
            Literal["MALFORMED"]
            | Literal["MODEL_UNAVAILABLE"]
            | Literal["NO_CHANGE_DIGEST"]
            | Literal["NOT_REQUESTED"]
            | Literal["REJECTED"]
            | Literal["UNGROUNDED"]
            | str
        )
        if isinstance(self.prose_outcome, ProseOutcomeType0):
            prose_outcome = self.prose_outcome.value
        else:
            prose_outcome = self.prose_outcome

        base_sha: None | str | Unset
        if isinstance(self.base_sha, Unset):
            base_sha = UNSET
        else:
            base_sha = self.base_sha

        prose: dict[str, Any] | None | Unset
        if isinstance(self.prose, Unset):
            prose = UNSET
        elif isinstance(self.prose, Prose):
            prose = self.prose.to_dict()
        else:
            prose = self.prose

        route: None | str | Unset
        if isinstance(self.route, Unset):
            route = UNSET
        elif isinstance(self.route, SummaryRoute):
            route = self.route.value
        else:
            route = self.route

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "head_sha": head_sha,
                "prose_outcome": prose_outcome,
            }
        )
        if base_sha is not UNSET:
            field_dict["base_sha"] = base_sha
        if prose is not UNSET:
            field_dict["prose"] = prose
        if route is not UNSET:
            field_dict["route"] = route

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_fact import FileFact  # noqa: PLC0415
        from ..models.prose import Prose  # noqa: PLC0415

        d = dict(src_dict)
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = FileFact.from_dict(files_item_data)

            files.append(files_item)

        head_sha = d.pop("head_sha")

        def _parse_prose_outcome(
            data: object,
        ) -> (
            Literal["MALFORMED"]
            | Literal["MODEL_UNAVAILABLE"]
            | Literal["NO_CHANGE_DIGEST"]
            | Literal["NOT_REQUESTED"]
            | Literal["REJECTED"]
            | Literal["UNGROUNDED"]
            | ProseOutcomeType0
        ):
            try:
                if not isinstance(data, str):
                    raise TypeError()
                componentsschemas_prose_outcome_type_0 = ProseOutcomeType0(data)

                return componentsschemas_prose_outcome_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NO_CHANGE_DIGEST"):
                    raise TypeError()
                componentsschemas_prose_outcome_type_1 = cast(Literal["NO_CHANGE_DIGEST"], data)
                if componentsschemas_prose_outcome_type_1 != "NO_CHANGE_DIGEST":
                    raise ValueError(
                        f"/components/schemas/ProseOutcome_type_1 must match const 'NO_CHANGE_DIGEST', got '{componentsschemas_prose_outcome_type_1}'"
                    )
                return componentsschemas_prose_outcome_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "NOT_REQUESTED"):
                    raise TypeError()
                componentsschemas_prose_outcome_type_2 = cast(Literal["NOT_REQUESTED"], data)
                if componentsschemas_prose_outcome_type_2 != "NOT_REQUESTED":
                    raise ValueError(
                        f"/components/schemas/ProseOutcome_type_2 must match const 'NOT_REQUESTED', got '{componentsschemas_prose_outcome_type_2}'"
                    )
                return componentsschemas_prose_outcome_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "MODEL_UNAVAILABLE"):
                    raise TypeError()
                componentsschemas_prose_outcome_type_3 = cast(Literal["MODEL_UNAVAILABLE"], data)
                if componentsschemas_prose_outcome_type_3 != "MODEL_UNAVAILABLE":
                    raise ValueError(
                        f"/components/schemas/ProseOutcome_type_3 must match const 'MODEL_UNAVAILABLE', got '{componentsschemas_prose_outcome_type_3}'"
                    )
                return componentsschemas_prose_outcome_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "MALFORMED"):
                    raise TypeError()
                componentsschemas_prose_outcome_type_4 = cast(Literal["MALFORMED"], data)
                if componentsschemas_prose_outcome_type_4 != "MALFORMED":
                    raise ValueError(
                        f"/components/schemas/ProseOutcome_type_4 must match const 'MALFORMED', got '{componentsschemas_prose_outcome_type_4}'"
                    )
                return componentsschemas_prose_outcome_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not (type(data) is str and data == "REJECTED"):
                    raise TypeError()
                componentsschemas_prose_outcome_type_5 = cast(Literal["REJECTED"], data)
                if componentsschemas_prose_outcome_type_5 != "REJECTED":
                    raise ValueError(
                        f"/components/schemas/ProseOutcome_type_5 must match const 'REJECTED', got '{componentsschemas_prose_outcome_type_5}'"
                    )
                return componentsschemas_prose_outcome_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not (type(data) is str and data == "UNGROUNDED"):
                raise TypeError()
            componentsschemas_prose_outcome_type_6 = cast(Literal["UNGROUNDED"], data)
            if componentsschemas_prose_outcome_type_6 != "UNGROUNDED":
                raise ValueError(
                    f"/components/schemas/ProseOutcome_type_6 must match const 'UNGROUNDED', got '{componentsschemas_prose_outcome_type_6}'"
                )
            return componentsschemas_prose_outcome_type_6

        prose_outcome = _parse_prose_outcome(d.pop("prose_outcome"))

        def _parse_base_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_sha = _parse_base_sha(d.pop("base_sha", UNSET))

        def _parse_prose(data: object) -> None | Prose | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                prose_type_0 = Prose.from_dict(data)

                return prose_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Prose | Unset, data)

        prose = _parse_prose(d.pop("prose", UNSET))

        def _parse_route(data: object) -> None | SummaryRoute | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                route_type_0 = SummaryRoute(data)

                return route_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SummaryRoute | Unset, data)

        route = _parse_route(d.pop("route", UNSET))

        change_summary = cls(
            files=files,
            head_sha=head_sha,
            prose_outcome=prose_outcome,
            base_sha=base_sha,
            prose=prose,
            route=route,
        )

        change_summary.additional_properties = d
        return change_summary

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
