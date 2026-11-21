from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.spend_account_kind import SpendAccountKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="SpendExportRow")


@_attrs_define
class SpendExportRow:
    """UTC daily debit totals using only the account and transport recorded at
    charge time, each split by what paid for it as Billing's Usage splits it.

       Attributes:
           account_kind (SpendAccountKind):
           dataset_version (int): The row contract version, always `1`.
           day (datetime.datetime): UTC midnight. The requested window can cover only part of this day.
           debits (int): The number of debits summed into this row.
           microcredits (int): Exact integer charge units; one credit contains one million microcredits.
           organization_id (UUID): The organization charged.
           account (None | str | Unset): Recorded attribution, not a current credential label or inferred account.
           free_review_microcredits (int | Unset): The part the free review month paid: this organization's
                `free-review:{debit}` grants for the row's debits. Default: 0.
           organization_microcredits (int | Unset): The part the organization's shared credit balance paid. Default: 0.
           own_key_microcredits (int | Unset): The part run on this organization's own provider key: a tariff
                equivalent its provider bills, not credit spend. The four funding
                columns add up to `microcredits`. Default: 0.
           plan_microcredits (int | Unset): The part of `microcredits` the workspace allowance or the author's seat paid.
               Default: 0.
           transport (None | str | Unset): The model transport recorded at charge time, null when the debit records none.
    """

    account_kind: SpendAccountKind
    dataset_version: int
    day: datetime.datetime
    debits: int
    microcredits: int
    organization_id: UUID
    account: None | str | Unset = UNSET
    free_review_microcredits: int | Unset = 0
    organization_microcredits: int | Unset = 0
    own_key_microcredits: int | Unset = 0
    plan_microcredits: int | Unset = 0
    transport: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        account_kind = self.account_kind.value

        dataset_version = self.dataset_version

        day = self.day.isoformat()

        debits = self.debits

        microcredits = self.microcredits

        organization_id = str(self.organization_id)

        account: None | str | Unset
        if isinstance(self.account, Unset):
            account = UNSET
        else:
            account = self.account

        free_review_microcredits = self.free_review_microcredits

        organization_microcredits = self.organization_microcredits

        own_key_microcredits = self.own_key_microcredits

        plan_microcredits = self.plan_microcredits

        transport: None | str | Unset
        if isinstance(self.transport, Unset):
            transport = UNSET
        else:
            transport = self.transport

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "account_kind": account_kind,
                "dataset_version": dataset_version,
                "day": day,
                "debits": debits,
                "microcredits": microcredits,
                "organization_id": organization_id,
            }
        )
        if account is not UNSET:
            field_dict["account"] = account
        if free_review_microcredits is not UNSET:
            field_dict["free_review_microcredits"] = free_review_microcredits
        if organization_microcredits is not UNSET:
            field_dict["organization_microcredits"] = organization_microcredits
        if own_key_microcredits is not UNSET:
            field_dict["own_key_microcredits"] = own_key_microcredits
        if plan_microcredits is not UNSET:
            field_dict["plan_microcredits"] = plan_microcredits
        if transport is not UNSET:
            field_dict["transport"] = transport

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        account_kind = SpendAccountKind(d.pop("account_kind"))

        dataset_version = d.pop("dataset_version")

        day = datetime.datetime.fromisoformat(d.pop("day"))

        debits = d.pop("debits")

        microcredits = d.pop("microcredits")

        organization_id = UUID(d.pop("organization_id"))

        def _parse_account(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        account = _parse_account(d.pop("account", UNSET))

        free_review_microcredits = d.pop("free_review_microcredits", UNSET)

        organization_microcredits = d.pop("organization_microcredits", UNSET)

        own_key_microcredits = d.pop("own_key_microcredits", UNSET)

        plan_microcredits = d.pop("plan_microcredits", UNSET)

        def _parse_transport(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        transport = _parse_transport(d.pop("transport", UNSET))

        spend_export_row = cls(
            account_kind=account_kind,
            dataset_version=dataset_version,
            day=day,
            debits=debits,
            microcredits=microcredits,
            organization_id=organization_id,
            account=account,
            free_review_microcredits=free_review_microcredits,
            organization_microcredits=organization_microcredits,
            own_key_microcredits=own_key_microcredits,
            plan_microcredits=plan_microcredits,
            transport=transport,
        )

        spend_export_row.additional_properties = d
        return spend_export_row

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
