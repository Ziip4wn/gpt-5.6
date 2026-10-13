from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..harness import Harness


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    name: str
    passed: bool
    details: tuple[str, ...]
    response: str


@dataclass(frozen=True, slots=True)
class ScenarioReport:
    results: tuple[ScenarioResult, ...]

    @property
    def passed(self) -> int:
        return sum(result.passed for result in self.results)

    @property
    def total(self) -> int:
        return len(self.results)


class ScenarioRunner:
    def __init__(self, harness: Harness) -> None:
        self.harness = harness

    def run_file(self, path: str | Path) -> ScenarioReport:
        scenario_path = Path(path)
        raw = json.loads(scenario_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("Le fichier de scénarios doit contenir une liste JSON")
        results = tuple(self._run_one(item) for item in raw)
        return ScenarioReport(results=results)

    def _run_one(self, scenario: dict[str, Any]) -> ScenarioResult:
        name = str(scenario.get("name", "sans_nom"))
        prompt = scenario.get("input")
        if not isinstance(prompt, str):
            raise ValueError(f"Le scénario {name!r} n'a pas de champ input valide")

        self.harness.memory.clear()
        response = self.harness.run(prompt).text
        folded = response.casefold()
        details: list[str] = []

        for expected in scenario.get("must_contain", []):
            if str(expected).casefold() not in folded:
                details.append(f"fragment absent : {expected!r}")
        for forbidden in scenario.get("must_not_contain", []):
            if str(forbidden).casefold() in folded:
                details.append(f"fragment interdit présent : {forbidden!r}")
        minimum = int(scenario.get("min_length", 0))
        if len(response.strip()) < minimum:
            details.append(f"longueur {len(response.strip())} < {minimum}")

        return ScenarioResult(
            name=name,
            passed=not details,
            details=tuple(details) or ("attentes satisfaites",),
            response=response,
        )

