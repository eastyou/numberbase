"""命令行测试。"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from numberbase.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class ConvertCommandTest(unittest.TestCase):
    def test_decimal_to_hex(self):
        code, out, _ = run_cli(["convert", "255", "--to", "16"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "ff")

    def test_hex_to_binary(self):
        code, out, _ = run_cli(["convert", "ff", "--from", "16", "--to", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "11111111")

    def test_uppercase_flag(self):
        code, out, _ = run_cli(["convert", "255", "--to", "16", "--upper"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "FF")

    def test_invalid_base_exit_code(self):
        code, _, err = run_cli(["convert", "10", "--to", "1"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_invalid_digit_exit_code(self):
        code, _, err = run_cli(["convert", "9", "--from", "8", "--to", "2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)


class SheetCommandTest(unittest.TestCase):
    def test_writes_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "sheet.html")
            code, out, _ = run_cli(
                ["sheet", "--count", "6", "--seed", "5", "-o", target]
            )
            self.assertEqual(code, 0)
            self.assertIn("已写入", out)
            with open(target, encoding="utf-8") as handle:
                html = handle.read()
            self.assertIn('class="item"', html)
            self.assertEqual(html.count('class="item"'), 6)

    def test_prints_to_stdout(self):
        code, out, _ = run_cli(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)

    def test_answers_flag(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--seed", "1", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_custom_title(self):
        code, out, _ = run_cli(["sheet", "--count", "2", "--title", "二进制小测"])
        self.assertEqual(code, 0)
        self.assertIn("二进制小测", out)

    def test_same_base_exit_code(self):
        code, _, err = run_cli(["sheet", "--from", "2", "--to", "2"])
        self.assertEqual(code, 2)
        self.assertIn("不能相同", err)

    def test_count_too_large_exit_code(self):
        code, _, err = run_cli(["sheet", "--count", "10", "--low", "0", "--high", "5"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_seed_is_reproducible(self):
        _, first, _ = run_cli(["sheet", "--count", "5", "--seed", "99"])
        _, second, _ = run_cli(["sheet", "--count", "5", "--seed", "99"])
        self.assertEqual(first, second)

    def test_nested_output_directory_created(self):
        with tempfile.TemporaryDirectory() as folder:
            target = os.path.join(folder, "a", "b", "sheet.html")
            code, _, _ = run_cli(["sheet", "--count", "2", "-o", target])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(target))


class HelpTest(unittest.TestCase):
    def test_help_exits_zero(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_subcommand_help(self):
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                main(["sheet", "--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
