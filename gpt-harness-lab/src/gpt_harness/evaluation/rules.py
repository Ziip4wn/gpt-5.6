from __future__ import annotations

from ..domain import CheckResult, Evaluation


def evaluate_response(text: str) -> Evaluation:
    stripped = text.strip()
    placeholder_tokens = ("TODO", "Lorem ipsum", "[insérer")
    checks = (
        CheckResult("non_empty", bool(stripped), "La réponse contient du texte."),
        CheckResult(
            "reasonable_length",
            len(stripped) <= 20_000,
            f"Longueur : {len(stripped)} caractères.",
        ),
        CheckResult(
            "no_placeholder",
            not any(token.casefold() in stripped.casefold() for token in placeholder_tokens),
            "Aucun marqueur de brouillon détecté.",
        ),
    )
    return Evaluation(checks=checks)

