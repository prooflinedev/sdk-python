from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.run_now_refusal_view_type_0 import RunNowRefusalViewType0
    from ..models.run_now_refusal_view_type_1 import RunNowRefusalViewType1
    from ..models.run_now_refusal_view_type_2 import RunNowRefusalViewType2
    from ..models.run_now_refusal_view_type_3 import RunNowRefusalViewType3
    from ..models.run_now_refusal_view_type_4 import RunNowRefusalViewType4
    from ..models.run_now_refusal_view_type_5 import RunNowRefusalViewType5
    from ..models.run_now_refusal_view_type_6 import RunNowRefusalViewType6
    from ..models.run_now_refusal_view_type_7 import RunNowRefusalViewType7
    from ..models.run_now_refusal_view_type_8 import RunNowRefusalViewType8
    from ..models.run_now_refusal_view_type_9 import RunNowRefusalViewType9
    from ..models.run_now_refusal_view_type_10 import RunNowRefusalViewType10
    from ..models.run_now_refusal_view_type_11 import RunNowRefusalViewType11


T = TypeVar("T", bound="RunNowRefused")


@_attrs_define
class RunNowRefused:
    """A run-now request that created nothing, as the 400 it is answered with.

    The refusal is a configuration fact, not a failure, and it is still sent
    as an RFC 9457 problem: `title`, `status` and `detail` are what a client
    that knows only problems shows, and `repository_name` and `refusal` are
    the extension members a client that knows refusals links from. During a
    rollout a page loaded from the previous bundle keeps working against
    this server, because a refusal was a 400 with a `detail` before too.

       Attributes:
           detail (str): One sentence naming the condition and the setting to change, for a
                reader with no link to follow.
           refusal (RunNowRefusalViewType0 | RunNowRefusalViewType1 | RunNowRefusalViewType10 | RunNowRefusalViewType11 |
               RunNowRefusalViewType2 | RunNowRefusalViewType3 | RunNowRefusalViewType4 | RunNowRefusalViewType5 |
               RunNowRefusalViewType6 | RunNowRefusalViewType7 | RunNowRefusalViewType8 | RunNowRefusalViewType9): Why a run-
               now request created nothing, each reason with what the page
                needs to link the setting to change.
           repository_name (str): The repository's name within its owner, as its pages are addressed.
           status (int): Always 400.
           title (str): Always `invalid request`.
    """

    detail: str
    refusal: (
        RunNowRefusalViewType0
        | RunNowRefusalViewType1
        | RunNowRefusalViewType10
        | RunNowRefusalViewType11
        | RunNowRefusalViewType2
        | RunNowRefusalViewType3
        | RunNowRefusalViewType4
        | RunNowRefusalViewType5
        | RunNowRefusalViewType6
        | RunNowRefusalViewType7
        | RunNowRefusalViewType8
        | RunNowRefusalViewType9
    )
    repository_name: str
    status: int
    title: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.run_now_refusal_view_type_0 import RunNowRefusalViewType0  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_1 import RunNowRefusalViewType1  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_2 import RunNowRefusalViewType2  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_3 import RunNowRefusalViewType3  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_4 import RunNowRefusalViewType4  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_5 import RunNowRefusalViewType5  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_6 import RunNowRefusalViewType6  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_7 import RunNowRefusalViewType7  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_8 import RunNowRefusalViewType8  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_9 import RunNowRefusalViewType9  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_10 import RunNowRefusalViewType10  # noqa: PLC0415

        detail = self.detail

        refusal: dict[str, Any]
        if isinstance(self.refusal, RunNowRefusalViewType0):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType1):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType2):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType3):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType4):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType5):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType6):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType7):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType8):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType9):
            refusal = self.refusal.to_dict()
        elif isinstance(self.refusal, RunNowRefusalViewType10):
            refusal = self.refusal.to_dict()
        else:
            refusal = self.refusal.to_dict()

        repository_name = self.repository_name

        status = self.status

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detail": detail,
                "refusal": refusal,
                "repository_name": repository_name,
                "status": status,
                "title": title,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.run_now_refusal_view_type_0 import RunNowRefusalViewType0  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_1 import RunNowRefusalViewType1  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_2 import RunNowRefusalViewType2  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_3 import RunNowRefusalViewType3  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_4 import RunNowRefusalViewType4  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_5 import RunNowRefusalViewType5  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_6 import RunNowRefusalViewType6  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_7 import RunNowRefusalViewType7  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_8 import RunNowRefusalViewType8  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_9 import RunNowRefusalViewType9  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_10 import RunNowRefusalViewType10  # noqa: PLC0415
        from ..models.run_now_refusal_view_type_11 import RunNowRefusalViewType11  # noqa: PLC0415

        d = dict(src_dict)
        detail = d.pop("detail")

        def _parse_refusal(
            data: object,
        ) -> (
            RunNowRefusalViewType0
            | RunNowRefusalViewType1
            | RunNowRefusalViewType10
            | RunNowRefusalViewType11
            | RunNowRefusalViewType2
            | RunNowRefusalViewType3
            | RunNowRefusalViewType4
            | RunNowRefusalViewType5
            | RunNowRefusalViewType6
            | RunNowRefusalViewType7
            | RunNowRefusalViewType8
            | RunNowRefusalViewType9
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_0 = RunNowRefusalViewType0.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_1 = RunNowRefusalViewType1.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_2 = RunNowRefusalViewType2.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_3 = RunNowRefusalViewType3.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_4 = RunNowRefusalViewType4.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_5 = RunNowRefusalViewType5.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_6 = RunNowRefusalViewType6.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_7 = RunNowRefusalViewType7.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_8 = RunNowRefusalViewType8.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_9 = RunNowRefusalViewType9.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_9
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_run_now_refusal_view_type_10 = RunNowRefusalViewType10.from_dict(
                    data
                )

                return componentsschemas_run_now_refusal_view_type_10
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_run_now_refusal_view_type_11 = RunNowRefusalViewType11.from_dict(data)

            return componentsschemas_run_now_refusal_view_type_11

        refusal = _parse_refusal(d.pop("refusal"))

        repository_name = d.pop("repository_name")

        status = d.pop("status")

        title = d.pop("title")

        run_now_refused = cls(
            detail=detail,
            refusal=refusal,
            repository_name=repository_name,
            status=status,
            title=title,
        )

        run_now_refused.additional_properties = d
        return run_now_refused

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
