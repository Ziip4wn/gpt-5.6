"""Un petit framework d'orchestration pour modèles GPT."""

from .config import AppConfig, load_config
from .harness import Harness

__all__ = ["AppConfig", "Harness", "load_config"]
__version__ = "0.1.0"

