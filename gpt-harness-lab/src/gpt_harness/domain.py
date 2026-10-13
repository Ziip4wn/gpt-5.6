from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str
    tool_call_id: str | None = None


@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ProviderReply:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    continuation_token: str | None = None


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True, slots=True)
class Evaluation:
    checks: tuple[CheckResult, ...]

    @property
    def score(self) -> float:
        if not self.checks:
            return 1.0
        return sum(check.passed for check in self.checks) / len(self.checks)

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


@dataclass(frozen=True, slots=True)
class RunResult:
    run_id: str
    text: str
    tool_calls: int
    evaluation: Evaluation
    metadata: dict[str, Any] = field(default_factory=dict)

