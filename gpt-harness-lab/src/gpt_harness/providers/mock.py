from __future__ import annotations

import json
import re
from typing import Any
from uuid import uuid4

from ..domain import Message, ProviderReply, ToolCall

_CALCULATE = re.compile(
    r"(?:calcule|calculer|combien (?:font|fait))\s*[:]?\s*(.+?)[?.!]*$", re.IGNORECASE
)
_TOOL_COMMAND = re.compile(r"^/tool\s+([a-zA-Z0-9_-]+)\s+(.+)$", re.DOTALL)


class MockProvider:
    """Fournisseur déterministe pour les démonstrations et les tests hors réseau."""

    def __init__(self, model: str = "mock-gpt") -> None:
        self.model = model

    def generate(
        self,
        *,
        messages: list[Message],
        instructions: str,
        tools: list[dict[str, Any]],
        continuation_token: str | None = None,
    ) -> ProviderReply:
        del instructions, tools, continuation_token
        if not messages:
            return ProviderReply(text="Aucun message reçu.")

        last = messages[-1]
        if last.role == "tool":
            return ProviderReply(text=f"Résultat de l'outil : {last.content}")

        prompt = last.content.strip()
        command = _TOOL_COMMAND.match(prompt)
        if command:
            name, raw_arguments = command.groups()
            try:
                arguments = json.loads(raw_arguments)
            except json.JSONDecodeError:
                return ProviderReply(text="Commande /tool invalide : les arguments doivent être JSON.")
            return self._tool_call(name, arguments)

        calculation = _CALCULATE.search(prompt)
        if calculation:
            return self._tool_call("calculator", {"expression": calculation.group(1).strip()})

        lowered = prompt.casefold()
        if "heure" in lowered and ("utc" in lowered or "actuelle" in lowered):
            return self._tool_call("current_time", {})
        if lowered.startswith("statistiques du texte :"):
            return self._tool_call("text_stats", {"text": prompt.split(":", 1)[1].strip()})

        return ProviderReply(
            text=(
                "Réponse du mode mock : votre message a bien traversé le harness GPT "
                f"({len(prompt)} caractères)."
            )
        )

    @staticmethod
    def _tool_call(name: str, arguments: dict[str, Any]) -> ProviderReply:
        call = ToolCall(call_id=f"mock_{uuid4().hex[:10]}", name=name, arguments=arguments)
        return ProviderReply(tool_calls=(call,), continuation_token=f"mock_{uuid4().hex}")

