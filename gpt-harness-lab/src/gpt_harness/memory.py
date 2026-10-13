from __future__ import annotations

from collections import deque

from .domain import Message


class ConversationMemory:
    def __init__(self, max_messages: int = 12) -> None:
        if max_messages < 1:
            raise ValueError("max_messages doit être supérieur à zéro")
        self._messages: deque[Message] = deque(maxlen=max_messages)

    def add(self, message: Message) -> None:
        self._messages.append(message)

    def snapshot(self) -> list[Message]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)

