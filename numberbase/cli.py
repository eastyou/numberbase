"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import BaseError, build_worksheet, convert
from .render import render_worksheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="numberbase",
        description="进制转换与可打印练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="转换单个数字")
    convert_parser.add_argument("text", help="待转换的数字，例如 255 或 ff")
    convert_parser.add_argument("--from", dest="from_base", type=int, default=10, help="源进制，默认 10")
    convert_parser.add_argument("--to", dest="to_base", type=int, required=True, help="目标进制")
    convert_parser.add_argument("--upper", action="store_true", help="输出大写字母")

    sheet_parser = subparsers.add_parser("sheet", help="生成练习纸 HTML")
    sheet_parser.add_argument("--count", type=int, default=20, help="题目数量，默认 20")
    sheet_parser.add_argument("--from", dest="from_base", type=int, default=10, help="源进制，默认 10")
    sheet_parser.add_argument("--to", dest="to_base", type=int, default=2, help="目标进制，默认 2")
    sheet_parser.add_argument("--low", type=int, default=0, help="最小值，默认 0")
    sheet_parser.add_argument("--high", type=int, default=255, help="最大值，默认 255")
    sheet_parser.add_argument("--seed", type=int, default=None, help="随机种子，便于重现")
    sheet_parser.add_argument("--title", default="进制转换练习", help="练习纸标题")
    sheet_parser.add_argument("--answers", action="store_true", help="追加答案页")
    sheet_parser.add_argument("-o", "--output", default=None, help="输出文件，默认打印到终端")
    return parser


def _write_output(html_text: str, output: Optional[str]) -> None:
    if not output:
        print(html_text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    print("已写入 %s" % path)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "convert":
            print(convert(args.text, args.from_base, args.to_base, upper=args.upper))
            return 0
        items = build_worksheet(
            args.count,
            args.from_base,
            args.to_base,
            args.low,
            args.high,
            args.seed,
        )
        html_text = render_worksheet(items, args.title, include_answers=args.answers)
        _write_output(html_text, args.output)
        return 0
    except BaseError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
