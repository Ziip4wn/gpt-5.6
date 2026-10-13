from __future__ import annotations

from .config import AppConfig
from .harness import Harness
from .memory import ConversationMemory
from .prompt_loader import PromptLoader
from .providers.factory import build_provider
from .tools.builtin import build_default_registry
from .tracing import TraceWriter


def build_harness(config: AppConfig) -> Harness:
    return Harness(
        provider=build_provider(config.model),
        prompt_loader=PromptLoader(config.paths.prompts),
        prompt_names=config.harness.prompt_files,
        tools=build_default_registry(),
        memory=ConversationMemory(config.harness.memory_messages),
        tracer=TraceWriter(config.paths.traces, enabled=config.tracing_enabled),
        max_tool_rounds=config.harness.max_tool_rounds,
    )

