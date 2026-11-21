"""进制转换的核心逻辑：解析、格式化、题目生成与判分。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"
MIN_BASE = 2
MAX_BASE = 36


class BaseError(ValueError):
    """进制、数字或题目参数不合法。"""


def check_base(base: int) -> int:
    """校验进制范围，返回原值。"""
    if isinstance(base, bool) or not isinstance(base, int):
        raise BaseError("进制必须是整数")
    if base < MIN_BASE or base > MAX_BASE:
        raise BaseError("进制必须在 %d 到 %d 之间，收到 %d" % (MIN_BASE, MAX_BASE, base))
    return base


def digit_value(char: str) -> int:
    """把一个字符转成 0~35 的数值。"""
    if not isinstance(char, str) or len(char) != 1:
        raise BaseError("需要一个数字字符，收到 %r" % (char,))
    index = DIGITS.find(char.lower())
    if index < 0:
        raise BaseError("非法数字字符：%r" % char)
    return index


def parse_number(text: str, base: int = 10) -> int:
    """把任意进制的字符串解析成整数，支持下划线分组与正负号。"""
    check_base(base)
    if not isinstance(text, str):
        raise BaseError("数字必须是字符串")
    cleaned = text.strip().replace("_", "")
    if not cleaned:
        raise BaseError("数字不能为空")
    sign = 1
    if cleaned[0] in "+-":
        if cleaned[0] == "-":
            sign = -1
        cleaned = cleaned[1:]
    if not cleaned:
        raise BaseError("符号后面缺少数字")
    value = 0
    for char in cleaned.lower():
        digit = digit_value(char)
        if digit >= base:
            raise BaseError("字符 %r 不属于 %d 进制" % (char, base))
        value = value * base + digit
    return sign * value


def format_number(value: int, base: int = 10, upper: bool = False) -> str:
    """把整数格式化成指定进制，负号在最前。"""
    check_base(base)
    if isinstance(value, bool) or not isinstance(value, int):
        raise BaseError("数值必须是整数")
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    remaining = abs(value)
    chars = []
    while remaining:
        remaining, digit = divmod(remaining, base)
        chars.append(DIGITS[digit])
    text = "".join(reversed(chars))
    if upper:
        text = text.upper()
    return sign + text


def convert(text: str, from_base: int = 10, to_base: int = 10, upper: bool = False) -> str:
    """从一种进制转换到另一种进制。"""
    check_base(from_base)
    check_base(to_base)
    return format_number(parse_number(text, from_base), to_base, upper=upper)


@dataclass(frozen=True)
class WorksheetItem:
    """一道转换题。"""

    value: int
    from_base: int = 10
    to_base: int = 2

    def __post_init__(self) -> None:
        check_base(self.from_base)
        check_base(self.to_base)
        if self.from_base == self.to_base:
            raise BaseError("源进制与目标进制不能相同")

    @property
    def question(self) -> str:
        """题干文本，例如 255（10 进制）→（2 进制）。"""
        return "%d（%d 进制）→（%d 进制）" % (self.value, self.from_base, self.to_base)

    def answer(self, upper: bool = False) -> str:
        """标准答案。"""
        return format_number(self.value, self.to_base, upper=upper)


def build_worksheet(
    count: int,
    from_base: int = 10,
    to_base: int = 2,
    low: int = 0,
    high: int = 255,
    seed: Optional[int] = None,
) -> List[WorksheetItem]:
    """生成一组不重复的转换题。"""
    check_base(from_base)
    check_base(to_base)
    if from_base == to_base:
        raise BaseError("源进制与目标进制不能相同")
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise BaseError("题目数量必须是正整数")
    if low < 0:
        raise BaseError("数值范围不能包含负数")
    if high < low:
        raise BaseError("最大值不能小于最小值")
    span = high - low + 1
    if count > span:
        raise BaseError("范围内只有 %d 个不同整数，无法生成 %d 道不重复的题" % (span, count))
    rng = random.Random(seed)
    values = rng.sample(range(low, high + 1), count)
    return [WorksheetItem(value, from_base, to_base) for value in values]


def check_answer(item: WorksheetItem, text: str) -> bool:
    """判断学生的答案是否正确，忽略大小写与多余空白。"""
    try:
        value = parse_number(text, item.to_base)
    except BaseError:
        return False
    return value == item.value
