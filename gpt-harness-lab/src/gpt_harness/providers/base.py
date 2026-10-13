from __future__ import annotations

from typing import Any, Protocol

from ..domain import Message, ProviderReply


class Provider(Protocol):
    def generate(
        self,
        *,
        messages: list[Message],
        instructions: str,
        tools: list[dict[str, Any]],
        continuation_token: str | None = None,
    ) -> ProviderReply: ...

