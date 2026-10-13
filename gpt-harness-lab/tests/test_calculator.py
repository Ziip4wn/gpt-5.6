import unittest

from gpt_harness.tools.builtin import safe_calculate


class SafeCalculatorTests(unittest.TestCase):
    def test_operator_precedence(self) -> None:
        self.assertEqual(safe_calculate("12 * (3 + 2)"), 60)

    def test_rejects_code_execution(self) -> None:
        with self.assertRaises(ValueError):
            safe_calculate("__import__('os').getcwd()")

    def test_rejects_huge_exponent(self) -> None:
        with self.assertRaises(ValueError):
            safe_calculate("2 ** 100")


if __name__ == "__main__":
    unittest.main()

