from __future__ import annotations

import json
from typing import Any

from ..domain import Message, ProviderReply, ToolCall


class OpenAIProvider:
    """Adaptateur léger pour la Responses API, avec appels de fonctions locaux."""

    def __init__(self, model: str, max_output_tokens: int = 800) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Le fournisseur OpenAI nécessite : python -m pip install -e '.[openai]'"
            ) from exc
        self.client = OpenAI()
        self.model = model
        self.max_output_tokens = max_output_tokens

    def generate(
        self,
        *,
        messages: list[Message],
        instructions: str,
        tools: list[dict[str, Any]],
        continuation_token: str | None = None,
    ) -> ProviderReply:
        request: dict[str, Any] = {
            "model": self.model,
            "instructions": instructions,
            "tools": tools,
            "max_output_tokens": self.max_output_tokens,
            "store": True,
        }
        if continuation_token:
            request["previous_response_id"] = continuation_token
            request["input"] = [
                {
                    "type": "function_call_output",
                    "call_id": message.tool_call_id,
                    "output": message.content,
                }
                for message in _trailing_tool_messages(messages)
            ]
        else:
            request["input"] = [
                {"role": message.role, "content": message.content}
                for message in messages
                if message.role in {"user", "assistant"}
            ]

        try:
            response = self.client.responses.create(**request)
        except Exception as exc:
            raise RuntimeError(f"Échec de l'appel OpenAI : {exc}") from exc
        calls: list[ToolCall] = []
        for item in response.output:
            if item.type != "function_call":
                continue
            try:
                arguments = json.loads(item.arguments)
            except json.JSONDecodeError:
                arguments = {"_invalid_json": item.arguments}
            calls.append(
                ToolCall(call_id=item.call_id, name=item.name, arguments=arguments)
            )
        return ProviderReply(
            text=response.output_text or "",
            tool_calls=tuple(calls),
            continuation_token=response.id,
        )


def _trailing_tool_messages(messages: list[Message]) -> list[Message]:
    trailing: list[Message] = []
    for message in reversed(messages):
        if message.role != "tool":
            break
        trailing.append(message)
    trailing.reverse()
    return trailing

