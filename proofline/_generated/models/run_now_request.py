from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.run_now_mode import RunNowMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="RunNowRequest")


@_attrs_define
class RunNowRequest:
    """An empty body keeps the run-now behavior existing clients request.

    Attributes:
        mode (RunNowMode | Unset): Whether an explicit request may reuse a settled review of the live head.
    """

    mode: RunNowMode | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: RunNowMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = RunNowMode(_mode)

        run_now_request = cls(
            mode=mode,
        )

        return run_now_request
