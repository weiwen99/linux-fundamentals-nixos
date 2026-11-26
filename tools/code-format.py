#!/usr/bin/env python3
"""按 docs/code-style.md 检查与重排书中的代码块。

  tools/code-format.py           就地重排全部 nixcode 块，并清理其它块的空白
  tools/code-format.py --check   只检查；有非规范块时列出位置并以 1 退出

Nix 块以 `nixfmt --strict --width=82` 为唯一格式来源：块内容先按整文件解析，
失败时包一层属性集再解析（书中多数是模块片段，不是完整表达式）。格式化结果
再做一次幂等检查与括号对齐检查，任一不过即报错，不写回。

非 Nix 块（shell 会话、纯文本）不套格式化器：只把制表符换成两个空格、去掉
行尾空白，保证块内空白干净。

格式化器路径取自环境变量 NIXFMT，缺省用 PATH 里的 nixfmt。
"""

from __future__ import annotations

import argparse
import difflib
import unicodedata
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# 82 列：A4 版心 455pt，代码框去掉左右边距与底色内边距后 435pt，
# Recursive Mono 在 \small 下每字符 5.18pt，一行最多 83.9 个字符。
# 取 82 留一列余量，A4 上不会触发 minted 的自动折行。
WIDTH = "82"
# nixfmt 的 width 不含行首缩进，深层代码可能到 82 + 缩进 列。
# A4 代码框内宽 435pt，等宽 5.18pt/字符，硬上限 83 个半角字符；
# 汉字与全角标点按两个半角计。超过就会触发 minted 折行。
MAX_COLS = 83
TEX_DIRS = ("chapters", "appendix", "frontmatter")
BLOCK_RE = re.compile(
    r"\\begin\{(nixcode|shellsession|textcode)\}(\[[^\]]*\])?[ \t]*\n(.*?)\\end\{\1\}", re.S
)
BLOCK_HEAD_RE = re.compile(r"\\begin\{(?:nixcode|shellsession|textcode)\}")


class FmtError(Exception):
    pass


def nixfmt_path() -> str:
    p = os.environ.get("NIXFMT") or shutil.which("nixfmt")
    if not p or not os.access(p, os.X_OK):
        sys.exit(f"找不到可执行的 nixfmt（NIXFMT={p or '未设置'}）")
    return p


def run_nixfmt(src: str) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            [nixfmt_path(), "--strict", "--width=" + WIDTH, "-"],
            input=src, text=True, capture_output=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise FmtError("nixfmt 60 秒未返回")
    return r.returncode, r.stdout, r.stderr


def canonicalize(body: str) -> str:
    """nixfmt 规范化；只有绑定列表的片段包一层属性集再排。"""
    src = body.strip("\n") + "\n"
    rc, out, _ = run_nixfmt(src)
    if rc == 0:
        return out
    # 标记行强制属性集展开：只有一条绑定时 nixfmt 会把整个集合压成一行。
    rc, out, err = run_nixfmt("{\n# probe\n" + src + "}\n")
    if rc != 0:
        first = " / ".join(err.strip().splitlines()[:2])
        raise FmtError(f"nixfmt 解析失败（整文件与属性集包裹均失败）：{first}")
    out_lines = out.strip("\n").split("\n")
    if len(out_lines) == 1 and out_lines[0].startswith("{ ") and out_lines[0].endswith(" }"):
        return out_lines[0][2:-2] + "\n"
    if out_lines[0] != "{" or out_lines[-1] != "}" or out_lines[1].strip() != "# probe":
        raise FmtError("包裹后的输出格式不符合预期，放弃改写")
    inner = [l[2:] if l.startswith("  ") else l for l in out_lines[2:-1]]
    return "\n".join(inner) + "\n"


def fmt_nix(body: str) -> str:
    """把一段 Nix 源码排成 nixfmt 的规范形式，并确认输出稳定。"""
    out = canonicalize(body)
    if canonicalize(out) != out:
        raise FmtError("nixfmt 输出不幂等，说明输入超出格式化器覆盖范围")
    return out.rstrip("\n")


_PAIRS_OF = {")": "(", "]": "[", "}": "{"}


def bracket_pairs(text: str) -> list[tuple[str, int, int, int, int]]:
    """返回 (括号, 开行, 开列, 闭行, 闭列)，行列从 0 计。

    需要跨过注释、双引号字符串（含 ${} 插值）与 '' 缩进字符串，
    否则字符串里的括号会被误当成结构。片段可以有未闭合的括号，
    只返回已配对的部分。
    """
    pairs: list[tuple[str, int, int, int, int]] = []
    stack: list[tuple[str, int, int]] = []
    line = col = i = 0
    n = len(text)
    # 模式栈：code 正常代码；str 双引号；istr 缩进字符串；interp 插值。
    # interp 层记录进入时的括号深度，用来判断哪个 } 结束插值。
    modes: list[list] = [["code", 0]]

    def adv(k: int) -> None:
        nonlocal line, col, i
        for _ in range(k):
            if i < n and text[i] == "\n":
                line += 1
                col = 0
            else:
                col += 1
            i += 1

    while i < n:
        c = text[i]
        mode = modes[-1][0]
        if mode in ("code", "interp"):
            if c == "#":
                while i < n and text[i] != "\n":
                    adv(1)
                continue
            if text.startswith("/*", i):
                j = text.find("*/", i + 2)
                adv((n if j < 0 else j + 2) - i)
                continue
            if c == '"':
                modes.append(["str", len(stack)])
                adv(1)
                continue
            if text.startswith("''", i):
                modes.append(["istr", len(stack)])
                adv(2)
                continue
            if c == "}" and mode == "interp" and len(stack) == modes[-1][1]:
                modes.pop()  # 插值结束，回到字符串
                adv(1)
                continue
            if c in "([{":
                stack.append((c, line, col))
                adv(1)
                continue
            if c in ")]}":
                if not stack or stack[-1][0] != _PAIRS_OF[c]:
                    raise ValueError(f"第 {line + 1} 行括号不配对")
                _, ol, oc = stack.pop()
                pairs.append((c, ol, oc, line, col))
                adv(1)
                continue
            adv(1)
            continue
        if mode == "str":
            if c == "\\":
                adv(2)
                continue
            if text.startswith("${", i):
                modes.append(["interp", len(stack)])
                adv(2)
                continue
            if c == '"':
                modes.pop()
                adv(1)
                continue
            adv(1)
            continue
        # mode == "istr"：'' 后跟 ' 是转义，后跟 $ 是插值，其余才是结尾。
        if text.startswith("'''", i):
            adv(3)
            continue
        if text.startswith("''", i):
            nxt = text[i + 2] if i + 2 < n else ""
            if nxt == "$":
                modes.append(["interp", len(stack)])
                adv(3)
                continue
            if nxt != "'":
                modes.pop()
                adv(2)
                continue
        if text.startswith("${", i):
            modes.append(["interp", len(stack)])
            adv(2)
            continue
        adv(1)
    return pairs


def check_alignment(text: str) -> list[str]:
    """多行括号对：收尾括号单独起行，缩进与开启括号所在行的缩进相同。"""
    problems = []
    lines = text.split("\n")
    try:
        pairs = bracket_pairs(text)
    except ValueError as e:
        return [f"括号结构无法解析：{e}"]
    for ch, ol, oc, cl, cc in pairs:
        if ol == cl:
            continue
        # 连续收尾的括号会叠在一行（`]))`），只允许前面出现别的收尾括号。
        if lines[cl][:cc].strip(" )]}"):
            problems.append(f"第 {cl + 1} 行的 {ch} 前面不是空白或收尾括号")
            continue
        open_indent = len(lines[ol]) - len(lines[ol].lstrip())
        line_indent = len(lines[cl]) - len(lines[cl].lstrip())
        if line_indent != open_indent:
            problems.append(
                f"第 {cl + 1} 行的 {ch} 缩进 {line_indent} 与开启行缩进 {open_indent} 不同"
            )
    return problems


def display_width(line: str) -> int:
    """按版面上的列宽计数：全角字符占两列。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in line)


def clean_plain(body: str) -> str:
    """非 Nix 块：制表符换两个空格，去掉行尾空白与块尾空行。"""
    lines = body.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(line.expandtabs(2).rstrip() for line in lines)


def check_block(kind: str, body: str) -> tuple[str, list[str]]:
    """返回 (规范内容, 问题列表)。问题为空时规范内容与正文相同。"""
    if kind != "nixcode":
        want = clean_plain(body)
        problems = [] if body == want + "\n" else ["含制表符、行尾空白或块尾空行"]
        return want, problems
    try:
        want = fmt_nix(body)
    except FmtError as e:
        return body, [f"无法排版：{e}"]
    problems = []
    for no, line in enumerate(want.split("\n"), 1):
        cols = display_width(line)
        if cols > MAX_COLS:
            problems.append(f"第 {no} 行 {cols} 列，超过 {MAX_COLS} 列上限")
    for msg in check_alignment(want):
        problems.append("对齐：" + msg)
    if body != want + "\n":
        problems.append("内容与 nixfmt --strict 输出不一致")
    return want, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    files = [p for d in TEX_DIRS for p in sorted((ROOT / d).glob("*.tex"))]
    total = bad = unfixable = 0
    writes: list[tuple[Path, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        heads = len(BLOCK_HEAD_RE.findall(text))
        matches = list(BLOCK_RE.finditer(text))
        if heads != len(matches):
            # 认不出的块不会被检查，静默跳过等于放行，按失败处理。
            print(f"{path.relative_to(ROOT)}: 有 {heads} 个代码块，只认出 {len(matches)} 个")
            return 1
        out: list[str] = []
        pos = 0
        for m in matches:
            total += 1
            kind, body = m.group(1), m.group(3)
            where = f"{path.relative_to(ROOT)}:{text[: m.start()].count(chr(10)) + 1}"
            want, problems = check_block(kind, body)
            if not problems:
                continue
            bad += 1
            print(f"{where} [{kind}]")
            for p in problems:
                print(f"  {p}")
            if want == body:
                # 内容已等于格式化输出，剩下的（列宽、对齐）工具改不动。
                unfixable += 1
                continue
            if args.check:
                diff = difflib.unified_diff(
                    body.rstrip("\n").split("\n"), want.split("\n"),
                    fromfile="当前", tofile="格式化后", lineterm="", n=1,
                )
                for d in list(diff)[:24]:
                    print("  " + d)
                continue
            out.append(text[pos : m.start(3)])
            out.append(want + "\n")
            pos = m.end(3)
            if check_block(kind, want + "\n")[1]:
                unfixable += 1  # 写回后仍不合规：列宽或对齐要人工处理
        if out:
            out.append(text[pos:])
            writes.append((path, "".join(out)))
    if args.check:
        print(f"检查 {total} 个代码块：{bad} 个不合规")
        return 1 if bad else 0
    # 逐文件写临时文件再替换：中途失败不会留下改了一半的文件。
    for path, content in writes:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    print(f"重排 {total} 个代码块：{bad} 个不合规，改写 {len(writes)} 个文件")
    if unfixable:
        print(f"其中 {unfixable} 个块需要手工处理：列宽或对齐超出格式化器范围")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
