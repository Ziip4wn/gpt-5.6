import tempfile
import unittest
from pathlib import Path

from gpt_harness.prompt_loader import PromptLoader


class PromptLoaderTests(unittest.TestCase):
    def test_lists_and_renders_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            prompt = Path(directory) / "hello.gpt"
            prompt.write_text("Bonjour {{name}}", encoding="utf-8")
            loader = PromptLoader(Path(directory))
            self.assertEqual(loader.names(), ["hello"])
            self.assertEqual(loader.render("hello", {"name": "Ada"}), "Bonjour Ada")

    def test_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            loader = PromptLoader(Path(directory))
            with self.assertRaises(ValueError):
                loader.load("../secret")


if __name__ == "__main__":
    unittest.main()

