"""渲染层测试。"""

import unittest

from numberbase.model import WorksheetItem
from numberbase.render import render_worksheet


def sample_items():
    return [
        WorksheetItem(255, 10, 16),
        WorksheetItem(8, 10, 2),
        WorksheetItem(15, 10, 2),
    ]


class RenderWorksheetTest(unittest.TestCase):
    def test_html_skeleton(self):
        html = render_worksheet(sample_items())
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn('<meta charset="utf-8">', html)

    def test_default_title(self):
        html = render_worksheet(sample_items())
        self.assertIn("<h1>进制转换练习</h1>", html)

    def test_custom_title_is_escaped(self):
        html = render_worksheet(sample_items(), title="<进制> & 练习")
        self.assertIn("&lt;进制&gt; &amp; 练习", html)
        self.assertNotIn("<h1><进制>", html)

    def test_item_count(self):
        html = render_worksheet(sample_items())
        self.assertEqual(html.count('class="item"'), 3)

    def test_problem_text_and_bases(self):
        html = render_worksheet(sample_items())
        self.assertIn("255<sub>10</sub>", html)
        self.assertIn("<sub>16</sub>", html)
        self.assertIn("blank", html)

    def test_answers_hidden_by_default(self):
        html = render_worksheet(sample_items())
        self.assertNotIn("参考答案", html)

    def test_answers_included(self):
        html = render_worksheet(sample_items(), include_answers=True)
        self.assertIn("参考答案", html)
        self.assertIn("FF<sub>16</sub>", html)
        self.assertIn("1000<sub>2</sub>", html)

    def test_empty_items(self):
        html = render_worksheet([])
        self.assertIn("暂无题目", html)
        self.assertIn("共 0 题", html)

    def test_a4_print_style(self):
        html = render_worksheet(sample_items())
        self.assertIn("size: A4", html)
        self.assertIn("@media print", html)

    def test_total_count_text(self):
        html = render_worksheet(sample_items())
        self.assertIn("共 3 题", html)


if __name__ == "__main__":
    unittest.main()
