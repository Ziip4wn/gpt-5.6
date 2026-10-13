from pathlib import Path

from gpt_harness.bootstrap import build_harness
from gpt_harness.config import load_config


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    config = load_config(project / "configs" / "default.toml")
    harness = build_harness(config)

    result = harness.run("Calcule 7 * 8")
    print(result.text)
    print(f"run_id={result.run_id} score={result.evaluation.score:.0%}")


if __name__ == "__main__":
    main()

