from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define

T = TypeVar("T", bound="StartSession")


@_attrs_define
class StartSession:
    """
    Attributes:
        connection_id (UUID): The vendor connection to start the session with.
        prompt_digest (str): The `prompt_digest` of the prompt the person confirmed.
    """

    connection_id: UUID
    prompt_digest: str

    def to_dict(self) -> dict[str, Any]:
        connection_id = str(self.connection_id)

        prompt_digest = self.prompt_digest

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "connection_id": connection_id,
                "prompt_digest": prompt_digest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        connection_id = UUID(d.pop("connection_id"))

        prompt_digest = d.pop("prompt_digest")

        start_session = cls(
            connection_id=connection_id,
            prompt_digest=prompt_digest,
        )

        return start_session
