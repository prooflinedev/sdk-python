from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_session_connection import AgentSessionConnection
    from ..models.agent_session_target import AgentSessionTarget


T = TypeVar("T", bound="AgentSessionPromptType0")


@_attrs_define
class AgentSessionPromptType0:
    """
    Attributes:
        prompt_digest (str): SHA-256 of `untrusted_text`. A start names it, so the session
             sends what the person confirmed.
        status (Literal['AVAILABLE']):
        target (AgentSessionTarget): What a session is pinned to: the finding's own reviewed pull request.
        untrusted_text (str): The exact text a vendor receives: untrusted finding data with
             every protected value withheld.
        withheld_values (int): How many protected values were withheld from the prompt.
        connections (list[AgentSessionConnection] | Unset): The organization's active vendor connections that allowlist
            the
             target repository; absent when none does. A start names one of
             them as `connection_id`.
    """

    prompt_digest: str
    status: Literal["AVAILABLE"]
    target: AgentSessionTarget
    untrusted_text: str
    withheld_values: int
    connections: list[AgentSessionConnection] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        prompt_digest = self.prompt_digest

        status = self.status

        target = self.target.to_dict()

        untrusted_text = self.untrusted_text

        withheld_values = self.withheld_values

        connections: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.connections, Unset):
            connections = []
            for connections_item_data in self.connections:
                connections_item = connections_item_data.to_dict()
                connections.append(connections_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt_digest": prompt_digest,
                "status": status,
                "target": target,
                "untrusted_text": untrusted_text,
                "withheld_values": withheld_values,
            }
        )
        if connections is not UNSET:
            field_dict["connections"] = connections

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_session_connection import AgentSessionConnection  # noqa: PLC0415
        from ..models.agent_session_target import AgentSessionTarget  # noqa: PLC0415

        d = dict(src_dict)
        prompt_digest = d.pop("prompt_digest")

        status = cast(Literal["AVAILABLE"], d.pop("status"))
        if status != "AVAILABLE":
            raise ValueError(f"status must match const 'AVAILABLE', got '{status}'")

        target = AgentSessionTarget.from_dict(d.pop("target"))

        untrusted_text = d.pop("untrusted_text")

        withheld_values = d.pop("withheld_values")

        _connections = d.pop("connections", UNSET)
        connections: list[AgentSessionConnection] | Unset = UNSET
        if _connections is not UNSET:
            connections = []
            for connections_item_data in _connections:
                connections_item = AgentSessionConnection.from_dict(connections_item_data)

                connections.append(connections_item)

        agent_session_prompt_type_0 = cls(
            prompt_digest=prompt_digest,
            status=status,
            target=target,
            untrusted_text=untrusted_text,
            withheld_values=withheld_values,
            connections=connections,
        )

        agent_session_prompt_type_0.additional_properties = d
        return agent_session_prompt_type_0

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
