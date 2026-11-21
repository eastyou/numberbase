"""模型层测试。"""

import unittest

from numberbase.model import (
    BaseError,
    WorksheetItem,
    build_worksheet,
    check_answer,
    check_base,
    convert,
    digit_value,
    format_number,
    parse_number,
)


class CheckBaseTest(unittest.TestCase):
    def test_accepts_valid_bases(self):
        for base in (2, 3, 8, 10, 16, 35, 36):
            self.assertEqual(check_base(base), base)

    def test_rejects_too_small(self):
        with self.assertRaises(BaseError):
            check_base(1)

    def test_rejects_too_large(self):
        with self.assertRaises(BaseError):
            check_base(37)

    def test_rejects_non_integer(self):
        with self.assertRaises(BaseError):
            check_base("10")

    def test_rejects_bool(self):
        with self.assertRaises(BaseError):
            check_base(True)


class DigitValueTest(unittest.TestCase):
    def test_decimal_digits(self):
        for char in "0123456789":
            self.assertEqual(digit_value(char), int(char))

    def test_letters_lower_and_upper(self):
        self.assertEqual(digit_value("a"), 10)
        self.assertEqual(digit_value("A"), 10)
        self.assertEqual(digit_value("z"), 35)
        self.assertEqual(digit_value("Z"), 35)

    def test_rejects_symbol(self):
        with self.assertRaises(BaseError):
            digit_value("@")

    def test_rejects_multi_char(self):
        with self.assertRaises(BaseError):
            digit_value("ab")


class ParseNumberTest(unittest.TestCase):
    def test_decimal(self):
        self.assertEqual(parse_number("2026"), 2026)

    def test_binary(self):
        self.assertEqual(parse_number("1010", 2), 10)

    def test_octal(self):
        self.assertEqual(parse_number("777", 8), 511)

    def test_hex_lower(self):
        self.assertEqual(parse_number("ff", 16), 255)

    def test_hex_upper(self):
        self.assertEqual(parse_number("FF", 16), 255)

    def test_base36(self):
        self.assertEqual(parse_number("z", 36), 35)
        self.assertEqual(parse_number("10", 36), 36)

    def test_negative(self):
        self.assertEqual(parse_number("-101", 2), -5)

    def test_leading_plus(self):
        self.assertEqual(parse_number("+17", 8), 15)

    def test_whitespace_trimmed(self):
        self.assertEqual(parse_number("  42  "), 42)

    def test_underscore_grouping(self):
        self.assertEqual(parse_number("1111_0000", 2), 240)

    def test_empty_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("")

    def test_blank_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("   ")

    def test_sign_only_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("-")

    def test_invalid_character_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("12g", 16)

    def test_digit_out_of_base_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("2", 2)

    def test_invalid_base_rejected(self):
        with self.assertRaises(BaseError):
            parse_number("10", 1)


class FormatNumberTest(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_number(0), "0")
        self.assertEqual(format_number(0, 2), "0")

    def test_decimal(self):
        self.assertEqual(format_number(255), "255")

    def test_binary(self):
        self.assertEqual(format_number(10, 2), "1010")

    def test_hex_lower(self):
        self.assertEqual(format_number(255, 16), "ff")

    def test_hex_upper(self):
        self.assertEqual(format_number(255, 16, upper=True), "FF")

    def test_negative(self):
        self.assertEqual(format_number(-10, 2), "-1010")

    def test_base36(self):
        self.assertEqual(format_number(35, 36), "z")
        self.assertEqual(format_number(36, 36), "10")

    def test_invalid_base(self):
        with self.assertRaises(BaseError):
            format_number(10, 0)

    def test_non_integer_value(self):
        with self.assertRaises(BaseError):
            format_number("10")


class ConvertTest(unittest.TestCase):
    def test_decimal_to_hex(self):
        self.assertEqual(convert("255", 10, 16), "ff")

    def test_hex_to_binary(self):
        self.assertEqual(convert("ff", 16, 2), "11111111")

    def test_binary_to_decimal(self):
        self.assertEqual(convert("10000000", 2, 10), "128")

    def test_same_base(self):
        self.assertEqual(convert("777", 8, 8), "777")

    def test_negative_kept(self):
        self.assertEqual(convert("-10", 10, 2), "-1010")

    def test_upper_output(self):
        self.assertEqual(convert("255", 10, 16, upper=True), "FF")

    def test_roundtrip_all_bases(self):
        for base in range(2, 37):
            text = format_number(123456, base)
            self.assertEqual(parse_number(text, base), 123456)

    def test_invalid_input(self):
        with self.assertRaises(BaseError):
            convert("xyz", 10, 2)


class WorksheetTest(unittest.TestCase):
    def test_length(self):
        items = build_worksheet(12, seed=1)
        self.assertEqual(len(items), 12)

    def test_values_unique(self):
        items = build_worksheet(30, low=0, high=100, seed=2)
        values = [item.value for item in items]
        self.assertEqual(len(set(values)), 30)

    def test_values_in_range(self):
        items = build_worksheet(20, low=10, high=29, seed=3)
        for item in items:
            self.assertGreaterEqual(item.value, 10)
            self.assertLessEqual(item.value, 29)

    def test_deterministic_with_seed(self):
        first = build_worksheet(8, seed=42)
        second = build_worksheet(8, seed=42)
        self.assertEqual([item.value for item in first], [item.value for item in second])

    def test_different_seeds_differ(self):
        first = build_worksheet(8, low=0, high=1000, seed=42)
        second = build_worksheet(8, low=0, high=1000, seed=43)
        self.assertNotEqual([item.value for item in first], [item.value for item in second])

    def test_question_and_answer(self):
        item = WorksheetItem(255, 10, 16)
        self.assertIn("255", item.question)
        self.assertEqual(item.answer(), "ff")
        self.assertEqual(item.answer(upper=True), "FF")

    def test_count_larger_than_span(self):
        with self.assertRaises(BaseError):
            build_worksheet(5, low=0, high=3)

    def test_zero_count_rejected(self):
        with self.assertRaises(BaseError):
            build_worksheet(0)

    def test_negative_low_rejected(self):
        with self.assertRaises(BaseError):
            build_worksheet(3, low=-5, high=5)

    def test_high_below_low_rejected(self):
        with self.assertRaises(BaseError):
            build_worksheet(3, low=10, high=5)

    def test_same_base_rejected(self):
        with self.assertRaises(BaseError):
            build_worksheet(3, 2, 2)

    def test_item_same_base_rejected(self):
        with self.assertRaises(BaseError):
            WorksheetItem(10, 10, 10)


class CheckAnswerTest(unittest.TestCase):
    def test_correct(self):
        item = WorksheetItem(255, 10, 16)
        self.assertTrue(check_answer(item, "ff"))

    def test_correct_uppercase(self):
        item = WorksheetItem(255, 10, 16)
        self.assertTrue(check_answer(item, "FF"))

    def test_leading_zero_accepted(self):
        item = WorksheetItem(5, 10, 2)
        self.assertTrue(check_answer(item, "0101"))

    def test_wrong_value(self):
        item = WorksheetItem(255, 10, 16)
        self.assertFalse(check_answer(item, "fe"))

    def test_invalid_text(self):
        item = WorksheetItem(255, 10, 16)
        self.assertFalse(check_answer(item, "gg"))

    def test_empty_text(self):
        item = WorksheetItem(255, 10, 16)
        self.assertFalse(check_answer(item, " "))


if __name__ == "__main__":
    unittest.main()
