"""Tests for main.py — The Worst App Idea Ever Pitched.

Gate (RULES.txt): /output/entry.txt must be UTF-8 text of 1-240 characters,
not only whitespace. The entry is one sentence pitching the worst app idea.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(REPO, "main.py")


def load_main():
    spec = importlib.util.spec_from_file_location("main_under_test", MAIN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGateValidation(unittest.TestCase):
    def setUp(self):
        self.main = load_main()

    def test_pitch_is_valid(self):
        self.assertTrue(self.main.validate_entry(self.main.PITCH))

    def test_pitch_is_one_sentence(self):
        self.assertEqual(self.main.PITCH.count("."), 1)
        self.assertNotIn("\n", self.main.PITCH)

    def test_pitch_within_brief_cap(self):
        # Brief caps the line at 200 chars; RULES gate allows 240.
        self.assertLessEqual(len(self.main.PITCH), 200)

    def test_empty_rejected(self):
        self.assertFalse(self.main.validate_entry(""))

    def test_whitespace_only_rejected(self):
        self.assertFalse(self.main.validate_entry("   \n\t  "))

    def test_over_240_rejected(self):
        self.assertFalse(self.main.validate_entry("x" * 241))

    def test_exactly_240_accepted(self):
        self.assertTrue(self.main.validate_entry("y" * 239 + "."))

    def test_double_space_rejected(self):
        self.assertFalse(self.main.validate_entry("Two  spaces here."))

    def test_missing_terminator_rejected(self):
        self.assertFalse(self.main.validate_entry("A sentence with no ending"))

    def test_single_char_accepted(self):
        self.assertTrue(self.main.validate_entry("!"))

    def test_multiline_rejected(self):
        self.assertFalse(self.main.validate_entry("First line.\nSecond line."))

    def test_non_string_rejected(self):
        self.assertFalse(self.main.validate_entry(None))
        self.assertFalse(self.main.validate_entry(42))
        self.assertFalse(self.main.validate_entry(b"bytes"))

    def test_leading_trailing_space_rejected(self):
        # A clean single sentence has no padding at either end.
        self.assertFalse(self.main.validate_entry(" padded. "))
        self.assertFalse(self.main.validate_entry("padded. "))

    def test_pitch_is_ascii(self):
        self.main.PITCH.encode("utf-8")
        self.assertTrue(self.main.PITCH.isascii())


class TestProgramRun(unittest.TestCase):
    def run_main(self, out_dir):
        env = dict(os.environ)
        env["MAKEFUN_OUTPUT_DIR"] = out_dir
        return subprocess.run(
            [sys.executable, MAIN], capture_output=True, text=True,
            timeout=30, env=env, cwd=REPO,
        )

    def test_writes_entry_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "output")
            result = self.run_main(out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            entry = os.path.join(out_dir, "entry.txt")
            self.assertTrue(os.path.isfile(entry))
            with open(entry, "r", encoding="utf-8") as f:
                text = f.read()
            self.assertEqual(text, self.main_pitch())

    def test_deterministic_across_two_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = os.path.join(tmp, "first")
            second = os.path.join(tmp, "second")
            self.assertEqual(self.run_main(first).returncode, 0)
            self.assertEqual(self.run_main(second).returncode, 0)
            with open(os.path.join(first, "entry.txt"), "rb") as f:
                a = f.read()
            with open(os.path.join(second, "entry.txt"), "rb") as f:
                b = f.read()
            self.assertEqual(a, b)

    def test_creates_missing_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "deep", "nested", "output")
            result = self.run_main(out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(os.path.isfile(os.path.join(out_dir, "entry.txt")))

    def test_overwrites_existing_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "output")
            os.makedirs(out_dir)
            with open(os.path.join(out_dir, "entry.txt"), "w") as f:
                f.write("stale content that must be replaced")
            result = self.run_main(out_dir)
            self.assertEqual(result.returncode, 0, result.stderr)
            with open(os.path.join(out_dir, "entry.txt"), "r", encoding="utf-8") as f:
                self.assertEqual(f.read(), self.main_pitch())

    def test_output_passes_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "output")
            self.assertEqual(self.run_main(out_dir).returncode, 0)
            with open(os.path.join(out_dir, "entry.txt"), "r", encoding="utf-8") as f:
                text = f.read()
            self.assertTrue(1 <= len(text) <= 240)
            self.assertTrue(text.strip())
            self.assertEqual(text.count("\n"), 0)

    def main_pitch(self):
        return load_main().PITCH


if __name__ == "__main__":
    unittest.main()
