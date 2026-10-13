from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from .bootstrap import build_harness
from .config import AppConfig, load_config
from .evaluation.scenarios import ScenarioRunner
from .prompt_loader import PromptLoader


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpt-harness", description="Mini-harness pour modèles GPT"
    )
    parser.add_argument("--config", default="configs/default.toml")
    parser.add_argument("--provider", choices=("mock", "openai"))
    parser.add_argument("--model")
    parser.add_argument("--no-trace", action="store_true")

    commands = parser.add_subparsers(dest="command", required=True)
    ask = commands.add_parser("ask", help="Envoyer une seule requête")
    ask.add_argument("text", nargs="+")
    commands.add_parser("chat", help="Ouvrir une conversation interactive")

    evaluate = commands.add_parser("eval", help="Exécuter des scénarios JSON")
    evaluate.add_argument("file")

    prompts = commands.add_parser("prompts", help="Inspecter les prompts .gpt")
    prompt_commands = prompts.add_subparsers(dest="prompt_command", required=True)
    prompt_commands.add_parser("list")
    show = prompt_commands.add_parser("show")
    show.add_argument("name")
    return parser


def _resolved_config(args: argparse.Namespace) -> AppConfig:
    config = load_config(args.config).with_overrides(provider=args.provider, model=args.model)
    if args.no_trace:
        config = replace(config, tracing_enabled=False)
    return config


def _print_result(result: object) -> None:
    text = getattr(result, "text")
    run_id = getattr(result, "run_id")
    tool_calls = getattr(result, "tool_calls")
    evaluation = getattr(result, "evaluation")
    print(text)
    print(f"\n[run {run_id[:8]} | outils {tool_calls} | score {evaluation.score:.0%}]")


def _chat(config: AppConfig) -> int:
    harness = build_harness(config)
    print("GPT Harness Lab — /quit pour quitter, /clear pour effacer la mémoire")
    while True:
        try:
            user_input = input("vous> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if user_input in {"/quit", "/exit"}:
            return 0
        if user_input == "/clear":
            harness.memory.clear()
            print("mémoire effacée")
            continue
        if not user_input:
            continue
        try:
            print(f"gpt> {harness.run(user_input).text}")
        except Exception as exc:
            print(f"erreur> {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        config = _resolved_config(args)
        if args.command == "prompts":
            loader = PromptLoader(config.paths.prompts)
            if args.prompt_command == "list":
                print("\n".join(loader.names()))
            else:
                print(loader.load(args.name))
            return 0

        harness = build_harness(config)
        if args.command == "ask":
            _print_result(harness.run(" ".join(args.text)))
            return 0
        if args.command == "chat":
            return _chat(config)
        if args.command == "eval":
            report = ScenarioRunner(harness).run_file(Path(args.file))
            for result in report.results:
                marker = "OK" if result.passed else "ECHEC"
                print(f"[{marker}] {result.name}: {'; '.join(result.details)}")
            print(f"\n{report.passed}/{report.total} scénarios réussis")
            return 0 if report.passed == report.total else 1
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

