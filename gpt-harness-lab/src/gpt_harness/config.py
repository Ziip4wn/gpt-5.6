from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelConfig:
    provider: str = "mock"
    name: str = "gpt-5.4"
    max_output_tokens: int = 800


@dataclass(frozen=True, slots=True)
class HarnessConfig:
    prompt_files: tuple[str, ...] = ("safety", "assistant")
    max_tool_rounds: int = 4
    memory_messages: int = 12


@dataclass(frozen=True, slots=True)
class PathConfig:
    prompts: Path
    traces: Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    model: ModelConfig
    harness: HarnessConfig
    paths: PathConfig
    tracing_enabled: bool = True

    def with_overrides(
        self, *, provider: str | None = None, model: str | None = None
    ) -> AppConfig:
        model_config = replace(
            self.model,
            provider=provider or self.model.provider,
            name=model or self.model.name,
        )
        return replace(self, model=model_config)


def _read_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _positive_int(value: Any, name: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} doit être un entier") from exc
    if parsed < 1:
        raise ValueError(f"{name} doit être supérieur à zéro")
    return parsed


def load_config(path: str | Path = "configs/default.toml") -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration introuvable : {config_path}")

    _read_dotenv(config_path.parent.parent / ".env")
    with config_path.open("rb") as stream:
        raw = tomllib.load(stream)

    model_raw = raw.get("model", {})
    harness_raw = raw.get("harness", {})
    paths_raw = raw.get("paths", {})
    trace_raw = raw.get("tracing", {})

    provider = os.getenv("GPT_HARNESS_PROVIDER", model_raw.get("provider", "mock"))
    model_name = os.getenv("GPT_HARNESS_MODEL", model_raw.get("name", "gpt-5.4"))
    if provider not in {"mock", "openai"}:
        raise ValueError("model.provider doit valoir 'mock' ou 'openai'")

    base = config_path.parent
    prompts = (base / paths_raw.get("prompts", "../prompts")).resolve()
    traces = (base / paths_raw.get("traces", "../.runs")).resolve()

    return AppConfig(
        model=ModelConfig(
            provider=provider,
            name=str(model_name),
            max_output_tokens=_positive_int(
                model_raw.get("max_output_tokens", 800), "model.max_output_tokens"
            ),
        ),
        harness=HarnessConfig(
            prompt_files=tuple(harness_raw.get("prompt_files", ["safety", "assistant"])),
            max_tool_rounds=_positive_int(
                harness_raw.get("max_tool_rounds", 4), "harness.max_tool_rounds"
            ),
            memory_messages=_positive_int(
                harness_raw.get("memory_messages", 12), "harness.memory_messages"
            ),
        ),
        paths=PathConfig(prompts=prompts, traces=traces),
        tracing_enabled=bool(trace_raw.get("enabled", True)),
    )

