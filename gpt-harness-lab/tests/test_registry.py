import unittest

from gpt_harness.tools.builtin import build_default_registry


class ToolRegistryTests(unittest.TestCase):
    def test_unknown_tool_is_structured_error(self) -> None:
        result = build_default_registry().execute("missing", {})
        self.assertFalse(result["ok"])
        self.assertIn("inconnu", result["error"])

    def test_text_stats(self) -> None:
        result = build_default_registry().execute("text_stats", {"text": "un deux\ntrois"})
        self.assertEqual(result["result"]["words"], 3)
        self.assertEqual(result["result"]["lines"], 2)


if __name__ == "__main__":
    unittest.main()

