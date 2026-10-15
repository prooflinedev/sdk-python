from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.run_now_mode import RunNowMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="RunNowRequest")


@_attrs_define
class RunNowRequest:
    """An empty body keeps the run-now behavior existing clients request.

    Attributes:
        focus_text (None | str | Unset): Optional investigation focus for EXTENDED, trimmed and frozen at admission.
             Limited to 500 UTF-16 code units.
        mode (RunNowMode | Unset): Whether an explicit request may reuse a settled review of the live head.
    """

    focus_text: None | str | Unset = UNSET
    mode: RunNowMode | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        focus_text: None | str | Unset
        if isinstance(self.focus_text, Unset):
            focus_text = UNSET
        else:
            focus_text = self.focus_text

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if focus_text is not UNSET:
            field_dict["focus_text"] = focus_text
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_focus_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        focus_text = _parse_focus_text(d.pop("focus_text", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: RunNowMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = RunNowMode(_mode)

        run_now_request = cls(
            focus_text=focus_text,
            mode=mode,
        )

        return run_now_request
