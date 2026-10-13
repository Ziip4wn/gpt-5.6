from __future__ import annotations

from ..config import ModelConfig
from .base import Provider
from .mock import MockProvider
from .openai_provider import OpenAIProvider


def build_provider(config: ModelConfig) -> Provider:
    if config.provider == "mock":
        return MockProvider(model=config.name)
    if config.provider == "openai":
        return OpenAIProvider(model=config.name, max_output_tokens=config.max_output_tokens)
    raise ValueError(f"Fournisseur inconnu : {config.provider}")

