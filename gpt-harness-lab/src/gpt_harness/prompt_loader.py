from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

_VARIABLE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")
_VALID_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")


class PromptLoader:
    def __init__(self, directory: Path) -> None:
        self.directory = directory.resolve()

    def names(self) -> list[str]:
        if not self.directory.is_dir():
            return []
        return sorted(path.stem for path in self.directory.glob("*.gpt") if path.is_file())

    def load(self, name: str) -> str:
        if not _VALID_NAME.fullmatch(name):
            raise ValueError(f"Nom de prompt invalide : {name!r}")
        path = self.directory / f"{name}.gpt"
        if not path.is_file():
            raise FileNotFoundError(f"Prompt introuvable : {path}")
        return path.read_text(encoding="utf-8").strip()

    def compose(self, names: tuple[str, ...] | list[str]) -> str:
        return "\n\n---\n\n".join(self.load(name) for name in names)

    def render(self, name: str, variables: Mapping[str, object]) -> str:
        template = self.load(name)

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in variables:
                raise KeyError(f"Variable de prompt manquante : {key}")
            return str(variables[key])

        return _VARIABLE.sub(replace, template)

