from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.declared_reach_outcome import DeclaredReachOutcome
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reach_gap_view import ReachGapView
    from ..models.reached_entity_view import ReachedEntityView


T = TypeVar("T", bound="DeclaredReachView")


@_attrs_define
class DeclaredReachView:
    """One assessment's declared reach receipt. A reached entity declares a
    dependency on what the change deploys; it is never a claim that the change
    breaks it.

       Attributes:
           complete (bool): Whether World's walk ended with no gap. An empty, incomplete reach
                says nothing about what depends on the change.
           entities (list[ReachedEntityView]): Every reached entity, shorter paths first, then by kind.
           gaps (list[ReachGapView]): Where World's walk or its evidence stopped.
           outcome (DeclaredReachOutcome):
           receipt_digest (None | str | Unset): World's digest of its full answer. Null unless `READ`.
           snapshot_id (None | Unset | UUID): The World snapshot the reach was read at. Null unless `READ`.
    """

    complete: bool
    entities: list[ReachedEntityView]
    gaps: list[ReachGapView]
    outcome: DeclaredReachOutcome
    receipt_digest: None | str | Unset = UNSET
    snapshot_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        complete = self.complete

        entities = []
        for entities_item_data in self.entities:
            entities_item = entities_item_data.to_dict()
            entities.append(entities_item)

        gaps = []
        for gaps_item_data in self.gaps:
            gaps_item = gaps_item_data.to_dict()
            gaps.append(gaps_item)

        outcome = self.outcome.value

        receipt_digest: None | str | Unset
        if isinstance(self.receipt_digest, Unset):
            receipt_digest = UNSET
        else:
            receipt_digest = self.receipt_digest

        snapshot_id: None | str | Unset
        if isinstance(self.snapshot_id, Unset):
            snapshot_id = UNSET
        elif isinstance(self.snapshot_id, UUID):
            snapshot_id = str(self.snapshot_id)
        else:
            snapshot_id = self.snapshot_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "complete": complete,
                "entities": entities,
                "gaps": gaps,
                "outcome": outcome,
            }
        )
        if receipt_digest is not UNSET:
            field_dict["receipt_digest"] = receipt_digest
        if snapshot_id is not UNSET:
            field_dict["snapshot_id"] = snapshot_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reach_gap_view import ReachGapView  # noqa: PLC0415
        from ..models.reached_entity_view import ReachedEntityView  # noqa: PLC0415

        d = dict(src_dict)
        complete = d.pop("complete")

        entities = []
        _entities = d.pop("entities")
        for entities_item_data in _entities:
            entities_item = ReachedEntityView.from_dict(entities_item_data)

            entities.append(entities_item)

        gaps = []
        _gaps = d.pop("gaps")
        for gaps_item_data in _gaps:
            gaps_item = ReachGapView.from_dict(gaps_item_data)

            gaps.append(gaps_item)

        outcome = DeclaredReachOutcome(d.pop("outcome"))

        def _parse_receipt_digest(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        receipt_digest = _parse_receipt_digest(d.pop("receipt_digest", UNSET))

        def _parse_snapshot_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                snapshot_id_type_0 = UUID(data)

                return snapshot_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        snapshot_id = _parse_snapshot_id(d.pop("snapshot_id", UNSET))

        declared_reach_view = cls(
            complete=complete,
            entities=entities,
            gaps=gaps,
            outcome=outcome,
            receipt_digest=receipt_digest,
            snapshot_id=snapshot_id,
        )

        declared_reach_view.additional_properties = d
        return declared_reach_view

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
