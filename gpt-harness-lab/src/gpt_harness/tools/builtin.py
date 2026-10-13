from __future__ import annotations

import ast
import operator
from datetime import UTC, datetime
from typing import Any

from .registry import Tool, ToolRegistry

_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_calculate(expression: str) -> int | float:
    if len(expression) > 200:
        raise ValueError("Expression trop longue")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node: ast.AST, depth: int = 0) -> int | float:
        if depth > 20:
            raise ValueError("Expression trop profonde")
        if isinstance(node, ast.Expression):
            return evaluate(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
            left = evaluate(node.left, depth + 1)
            right = evaluate(node.right, depth + 1)
            if isinstance(node.op, ast.Pow) and abs(right) > 12:
                raise ValueError("Exposant trop grand")
            result = _BINARY_OPERATORS[type(node.op)](left, right)
            if abs(result) > 1e100:
                raise ValueError("Résultat trop grand")
            return result
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
            return _UNARY_OPERATORS[type(node.op)](evaluate(node.operand, depth + 1))
        raise ValueError("Opération non autorisée")

    return evaluate(tree)


def _calculator(arguments: dict[str, Any]) -> int | float:
    expression = arguments.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("'expression' doit être une chaîne non vide")
    return safe_calculate(expression)


def _current_time(arguments: dict[str, Any]) -> str:
    del arguments
    return datetime.now(UTC).isoformat()


def _text_stats(arguments: dict[str, Any]) -> dict[str, int]:
    text = arguments.get("text")
    if not isinstance(text, str):
        raise ValueError("'text' doit être une chaîne")
    return {
        "characters": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()) or 1,
    }


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="calculator",
            description="Calcule une expression arithmétique sans exécuter de code arbitraire.",
            parameters={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
                "additionalProperties": False,
            },
            handler=_calculator,
        )
    )
    registry.register(
        Tool(
            name="current_time",
            description="Retourne l'heure actuelle en UTC au format ISO 8601.",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            handler=_current_time,
        )
    )
    registry.register(
        Tool(
            name="text_stats",
            description="Compte les caractères, mots et lignes d'un texte.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
            handler=_text_stats,
        )
    )
    return registry

