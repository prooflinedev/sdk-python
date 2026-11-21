from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.local_reverification_outcome import LocalReverificationOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.local_stored_check import LocalStoredCheck


T = TypeVar("T", bound="LocalReverification")


@_attrs_define
class LocalReverification:
    """One finding a patch review re-verified against the patch. The outcome is
    local: the pull request's finding is unchanged whatever it is.

       Attributes:
           checks (Any): Each deterministic check the finding cited and its result on the
                patched head. Empty until an outcome is recorded.
           finding_id (UUID): The finding being re-verified against this patch.
           iteration (int): The request's number among the requests to re-verify the finding's
                series on this patch, at most 3.
           outcome (LocalReverificationOutcome): `RESOLVED_VERIFIED` needs the re-investigation to reject the finding's
                hypothesis and every cited check to pass. `STILL_PRESENT`: the hypothesis
                is supported, or a check still finds the mechanism. `NOT_VERIFIED`:
                anything else, including a review that ended without an answer.
                `PENDING`: the review is still running.
           stored_check (LocalStoredCheck | None | Unset): The check a code reproduction stored for the finding, which a
               pushed
                head runs again; run its command against the local changes before
                pushing. The patch review does not run it. Absent for a finding with
                no stored check.
    """

    checks: Any
    finding_id: UUID
    iteration: int
    outcome: LocalReverificationOutcome
    stored_check: LocalStoredCheck | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.local_stored_check import LocalStoredCheck  # noqa: PLC0415

        checks = self.checks

        finding_id = str(self.finding_id)

        iteration = self.iteration

        outcome = self.outcome.value

        stored_check: dict[str, Any] | None | Unset
        if isinstance(self.stored_check, Unset):
            stored_check = UNSET
        elif isinstance(self.stored_check, LocalStoredCheck):
            stored_check = self.stored_check.to_dict()
        else:
            stored_check = self.stored_check

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "checks": checks,
                "finding_id": finding_id,
                "iteration": iteration,
                "outcome": outcome,
            }
        )
        if stored_check is not UNSET:
            field_dict["stored_check"] = stored_check

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.local_stored_check import LocalStoredCheck  # noqa: PLC0415

        d = dict(src_dict)
        checks = d.pop("checks")

        finding_id = UUID(d.pop("finding_id"))

        iteration = d.pop("iteration")

        outcome = LocalReverificationOutcome(d.pop("outcome"))

        def _parse_stored_check(data: object) -> LocalStoredCheck | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                stored_check_type_0 = LocalStoredCheck.from_dict(data)

                return stored_check_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(LocalStoredCheck | None | Unset, data)

        stored_check = _parse_stored_check(d.pop("stored_check", UNSET))

        local_reverification = cls(
            checks=checks,
            finding_id=finding_id,
            iteration=iteration,
            outcome=outcome,
            stored_check=stored_check,
        )

        local_reverification.additional_properties = d
        return local_reverification

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
