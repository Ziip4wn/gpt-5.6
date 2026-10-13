import tempfile
import unittest
from pathlib import Path

from gpt_harness.harness import Harness
from gpt_harness.memory import ConversationMemory
from gpt_harness.prompt_loader import PromptLoader
from gpt_harness.providers.mock import MockProvider
from gpt_harness.tools.builtin import build_default_registry
from gpt_harness.tracing import TraceWriter


class HarnessTests(unittest.TestCase):
    def _harness(self, root: Path) -> Harness:
        prompt_dir = root / "prompts"
        prompt_dir.mkdir()
        (prompt_dir / "assistant.gpt").write_text("Sois utile.", encoding="utf-8")
        return Harness(
            provider=MockProvider(),
            prompt_loader=PromptLoader(prompt_dir),
            prompt_names=("assistant",),
            tools=build_default_registry(),
            memory=ConversationMemory(4),
            tracer=TraceWriter(root / "runs"),
            max_tool_rounds=2,
        )

    def test_runs_tool_loop_and_writes_trace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = self._harness(root)
            result = harness.run("Calcule 6 * 7")
            self.assertIn("42", result.text)
            self.assertEqual(result.tool_calls, 1)
            self.assertTrue(result.evaluation.passed)
            self.assertTrue((root / "runs" / f"{result.run_id}.jsonl").is_file())

    def test_keeps_only_user_and_final_assistant_in_memory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            harness = self._harness(Path(directory))
            harness.run("Calcule 2 + 2")
            self.assertEqual([m.role for m in harness.memory.snapshot()], ["user", "assistant"])


if __name__ == "__main__":
    unittest.main()

