# numberbase

[![CI](https://github.com/eastyou/numberbase/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/numberbase/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

进制转换练习纸：把十进制、二进制、八进制、十六进制之间的互转变成可打印的 A4 练习，附独立答案页。

## 特性

- 支持 2~36 任意进制互转，字母大小写不敏感
- 一次生成整页题目，同页内不重复，可指定数值范围与随机种子
- `--answers` 输出独立答案页，老师打印一份即可
- 解析支持正负号、下划线分组与首尾空白，错误提示明确指出是哪个字符
- 纯标准库，零依赖，Windows / macOS / Linux 通用

## 安装

```bash
python -m pip install -e .
```

## 用法

转换单个数字：

```bash
numberbase convert 255 --to 16
numberbase convert ff --from 16 --to 2
numberbase convert -10 --to 2
```

生成练习纸：

```bash
numberbase sheet --count 20 --from 10 --to 2 --low 0 --high 255 --seed 7 -o worksheet.html --answers
```

`sheet` 的参数：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--count` | 题目数量 | 20 |
| `--from` | 源进制 | 10 |
| `--to` | 目标进制 | 2 |
| `--low` / `--high` | 数值范围 | 0 / 255 |
| `--seed` | 随机种子，便于重现同一份练习 | 无 |
| `--title` | 练习纸标题 | 进制转换练习 |
| `--answers` | 追加答案页 | 关闭 |
| `-o` | 输出文件 | 打印到终端 |

## 示例

[examples/numberbase.html](examples/numberbase.html) 是一份 20 题的十进制转二进制练习，带答案页。

## 测试

```bash
python -m unittest discover -s tests -v
```

## 协议

MIT © 2026 eastyou
