# 构建说明

## 四种版式

| 版式 | 纸张 | 字号 | 颜色 | 入口 |
|---|---|---|---|---|
| `screen` | A4 | 11pt | 彩色 | `variants/screen.tex` |
| `print` | A4，内侧加宽 | 11pt | 彩色 | `variants/print.tex` |
| `ereader` | 91mm × 122mm | 9pt | 灰度 | `variants/ereader.tex` |
| `phone` | 88mm × 176mm | 9pt | 彩色 | `variants/phone.tex` |

版式开关在 `tex/layout.tex`：`\booklayout` 决定 `\ifbknarrow`、`\ifbkgrayscale`、
`\ifbkprint` 与 `\bkside`，`main.tex` 把 `\bkfontsize`、`\bkside` 传给 `ctexbook`。
正文只有一份，版式差异全部落在 `tex/preamble.tex` 的条件分支里。

```sh
./build.sh              # 全部四种
./build.sh ereader      # 只构建一种
./build.sh clean        # 清理
```

编译开始前会跑 `tools/code-format.py --check`，核对每个 Nix 代码块是否与
`nixfmt --strict --width=82` 的输出一致，并检查括号对齐与 83 列上限（规则见
`docs/code-style.md`）。不合规时构建停止；`tools/code-format.py` 就地重排。
`clean` 不触发这项检查。

产物在 `build/<版式>/main-<版式>.pdf`。首次运行由 `nix build` 解析
TeX Live、poppler-utils、三个字体包、nixfmt 与 python3，写入 `build/env.sh` 与
`build/fonts.tex`；之后复用，不再联网。

## 窄版式的四条约束

窄页的版心很小：ereader 约 81 × 110 mm，phone 约 76 × 162 mm。代码块在
ereader 上每行容 51 列、phone 上 47 列，超过的代码行由 minted 折行（续行前有
折行符号），这是窄版式无法避免的；A4 两种版式的折行由 83 列上限挡住。四处机制必须避开：

1. 表格一律用 `booktable`（`xltabular` 的别名），并在 `booktable` 上挂
   `\AtBeginEnvironment` 把字号降到 `\scriptsize`。钩子必须挂在 `booktable`：
   `\AtBeginEnvironment` 改写的是 `\begin`，环境名写成 `xltabular` 时不生效。
2. 图与浮动体用 `\figfit` 包一层 `adjustbox`，同时限制宽与高
   （`max width=\linewidth`、`max height=0.72\textheight`）。只限宽时，高图会高于
   版心，`[H]` 放不下，会在 `\end{document}` 处反复输出空页。
3. 行内代码中的长标识符必须显式给出断点，写作 `\allowbreak{}`，
   例如 `\texttt{environment.\allowbreak{}systemPackages}`。
   花括号不是必需的：`\allowbreak` 后面的空格会被当成控制词结束符吞掉，
   两种写法排版结果相同，加 `{}` 只是让后续字符贴着断点、便于阅读源码。
4. 文字型长表在窄版式下改为列表。附录 E 的症状索引即如此：三列表在窄页上
   每行折成三行，窄列里代码与汉字大小不一，按行读不下去。

## 版面：为什么不用 needspace 宏包

早期版本用 `needspace` 让代码块与提示框不要贴着页底开始。这个宏包靠
`\penalty -100` 制造断点。页面后段一旦溢出，TeX 在代价比较中会选中这个断点，
即使当时只填了页面的四分之一，于是留下一大片空白。旧版的装虚拟机一章曾因此
出现一页只有九行正文。

现在改用 `\bookneedspace`（`tex/preamble.tex`）：直接比较 `\pagegoal-\pagetotal`
与所需高度，只在确实放不下时 `\newpage`。`\newpage` 本身带有 `\penalty-\@M`，
但它只在判断为放不下时执行，不会被代价比较提前选中。`booktable` 与 `\section`
也走这条检查：表格只需放下表头与两行数据，小节标题需放下标题与六行正文；
提示框不设预留（见下一节）。

`\section*` 不经过这层包装，frontmatter 里的无编号小节不受影响。

`booktable` 的表头由作者在第一个 `\midrule` 后手写 `\endhead`，跨页时重复表头。
新增表格须照此写，位置不对会导致表头只在首页出现。

## 已知问题：提示框整块后移留下的页尾空白

提示框默认不可分割：允许跨页时，框首或框尾常单独留在页边，只剩标题加一行，
比整块移到下一页更难读。代价是框放不下时整块后移，前一页留出空白。

例外是检查点框：章末检查点常有八条以上，窄版式下框高会超过版心。不可分割的框
一旦高于版心，TeX 会在页首反复重排，生成上万页空页。故窄版式的检查点允许跨页
（`\bkcheckbreak`），宽版式仍保持整块。新增提示框时若内容可能超过一页，
照此加一个窄版分支。

提示框不设高度预留，因为不可分割的框本来就会被 TeX 整块后移，预留只会让空白
出现得更早。代码块与表格仍保留预留：它们可以跨页，若不预留，末行或表头会单独
留在页底。

## 已知问题：窄版式的无限分页

窄版式（ereader、phone）几次出现构建卡住、页数涨到几十万页的情况。已确认的
三个来源：

1. 不可分割的提示框高于版心。检查点框条目多时触发，已改为窄版式可跨页。
2. 高图放不下。`[H]` 浮动体高于版心时无法放置，已在 `\figfit` 中限高。
3. 中间文件被污染。无限分页会把 `.aux`、`.toc` 写成垃圾（曾见到十四 MB 的 aux），
   之后每一遍编译都跟着失败，看起来像"改了也没用"。

现在的防护：`build.sh` 每次构建前删除该版式的旧 PDF，单遍限时十五分钟，
失败时清空 `build/<版式>` 目录。`main.tex` 在 `\end{document}` 前显式
`\clearpage`，先输出浮动体与表格再结束。

判断是否复发的方法：构建输出的页数与上一版相比暴涨，或 `build/<版式>/main-<版式>.xdv`
超过几十 MB。

## 已知问题：longtable 跨页时的无限胶收缩

任何跨页的 `longtable`/`xltabular` 都会在日志里报若干行：

```
Infinite glue shrinkage found in box being split
```

这不是本书宏的问题。最小复现只需 `book` 文档类、`longtable` 与一个跨页的长表，
去掉 `booktabs`、`\raggedbottom`、`\hline` 均照旧复现，见下表。

| 变体 | 结果 |
|---|---|
| `longtable` + `booktabs` + `\raggedbottom` | 报 1 次 |
| 去掉 `\raggedbottom` | 报 1 次 |
| 去掉 `booktabs` | 报 1 次 |
| 全部规则去掉，只有数据行 | 报 1 次 |

环境为 TeX Live 2025（`texlive-combined-full-2025-final`，XeTeX 0.999997），
观测日期 2026-11-25。对输出做过核对：80 行两页的表，用 `pdftotext` 统计仍有 80 行，
没有丢内容。因此按已知问题保留，不再为它改动表格机制。

## 交付前检查

```sh
for v in screen print ereader phone; do
  echo "$v: $(grep -c 'Overfull \\hbox' build/$v/main-$v.log) 处溢出"
done
```

`screen` 与 `print` 应为 0。窄版式目前留有若干处，来源是长标识符与窄列，
最大约 30pt。另需检查是否真有文字越出纸面：

```sh
python3 - <<'EOF'
import re, subprocess
for pdf in ['build/ereader/main-ereader.pdf', 'build/phone/main-phone.pdf']:
    n = int([l for l in subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
             .stdout.splitlines() if l.startswith('Pages')][0].split()[1])
    hits = []
    for p in range(1, n + 1):
        xml = subprocess.run(['pdftotext', '-bbox', '-f', str(p), '-l', str(p), pdf, '-'],
                             capture_output=True, text=True).stdout
        w = float(re.search(r'<page width="([\d.]+)"', xml).group(1))
        for m in re.finditer(r'xMax="([\d.]+)"', xml):
            if float(m.group(1)) > w - 2:
                hits.append((p, float(m.group(1))))
    print(pdf, len(hits), hits[:5])
EOF
```

## 已知问题：窄版式表格内的长标识符

行内代码在表格列里没有断点机制。连字符在等宽字体里不产生断点：TeX 只在字符
等于当前字体的 `\hyphenchar` 时才把 `-` 当作可断的显式连字符，而等宽字体通常
把 `\hyphenchar` 设为负值。`breakanywhere` 是 minted 的键，只管代码块，管不到
表格里的 `\texttt`。窄页的列宽只有二三十毫米，一个长标识符就顶出列宽。

实测（2026-11-26，`build.sh` 默认参数）：`screen` 0 处、`print` 0 处、
`ereader` 1 处、`phone` 2 处（最大 19.7pt）。窄版式表内已缩到
`\scriptsize`，表格一侧的叠字本轮清空；剩余几处来自代码块与正文里无法断开的
长 token，例如 `environment.systemPackages`、`configuration.`。

局部加 `\allowbreak` 有效，例：`\texttt{powerManagement.\allowbreak resumeCommands}`。
问题只在于全书六十来张表里哪些格子需要加，得逐格判断，且窄版式独有的断点
会把 A4 版的行高一起改掉。按已知问题保留。

日志里出现上面几条已知问题都不算失败。构建脚本以 PDF 是否生成为判据：
latexmk 因交叉引用未稳而以非零码结束是常态，未生成 PDF 才算失败；单遍限时
十五分钟，超时即失败。
