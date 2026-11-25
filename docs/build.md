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

产物在 `build/<版式>/main-<版式>.pdf`。首次运行由 `nix build` 解析
TeX Live、poppler-utils 与三个字体包，写入 `build/env.sh` 与 `build/fonts.tex`；
之后复用，不再联网。

## 窄版式的三条约束

窄页的版心只有七十余毫米，三处机制必须避开：

1. 表格一律用 `booktable`（`xltabular` 的别名），允许跨页。不可分割的
   `tabular` 一旦高于版心，LaTeX 会不断生成空页。
2. 图与浮动体用 `\figfit` 包一层 `adjustbox`，并在窄版式下强制 `H` 放置，
   避免浮动体超过版心高度后产生空浮动页。
3. 行内代码中的长标识符必须显式给出断点，写作 `\allowbreak{}`，
   例如 `\texttt{environment.\allowbreak{}systemPackages}`。
   花括号不是必需的：`\allowbreak` 后面的空格会被当成控制词结束符吞掉，
   两种写法排版结果相同，加 `{}` 只是让后续字符贴着断点、便于阅读源码。

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

`screen` 与 `print` 应为 0。窄版式目前各留有若干处，来源是表格列里的长标识符，
溢出量在 1pt 到 33pt 之间，溢出的那一段会压进右侧列（见下节）。

## 已知问题：窄版式表格内的长标识符

行内代码在表格列里没有断点机制。连字符在等宽字体里不产生断点：TeX 只在字符
等于当前字体的 `\hyphenchar` 时才把 `-` 当作可断的显式连字符，而等宽字体通常
把 `\hyphenchar` 设为负值。`breakanywhere` 是 minted 的键，只管代码块，管不到
表格里的 `\texttt`。窄页的列宽只有二三十毫米，一个长标识符就顶出列宽。

实测（2026-11-25，`build.sh` 默认参数）：`screen` 0 处、`print` 0 处、
`ereader` 7 处、`phone` 14 处，最大 33.2pt。那处在附录 E 症状索引表
（`appendix/e-symptoms.tex` 的 `nix-collect-garbage -{}-dry-run` 一行）：
`nix-collect-garbage` 宽 103.3pt，列宽 70.1pt，溢出的 21.2pt 压在第三列的「十五」
之上，两串字重叠。仍在纸面以内，不会裁切，但那一格不可读。

`appendix/e-symptoms.tex` 里 `powerManagement.\allowbreak resumeCommands`
用了手工断点，说明局部加 `\allowbreak` 确实有效；问题只在于全书 57 张表里
哪些格子需要加，得逐格判断，且窄版式独有的断点会把 A4 版的行高一起改掉。

另一条路是缩小窄版式的表内字号。`tex/preamble.tex` 里有一行
`\AtBeginEnvironment{xltabular}{\ifbknarrow\scriptsize\fi}`，但它对本书不生效：
etoolbox 的 `\AtBeginEnvironment` 是改写 `\begin`，只在环境名正是 `xltabular`
时插入钩子；本书写的是 `\begin{booktable}`（`\booktable` 是 `\let` 出来的别名），
名字对不上，钩子从不执行。最小复现：把钩子挂到 `booktable` 上，表内立刻落到
6.5pt；挂到 `xltabular` 上则仍是 10.5pt。因此窄版式表格目前与正文同为 9pt。

把键名改成 `booktable` 就能生效，但本书暂不走这条路：字号缩到 7.5pt 后，那处
33pt 的溢出按比例仍有 27pt，压进邻列的问题不消失，而 57 张表在窄页上整体变小
是另一笔可读性代价。要动的话，两者应当一起评估。

日志里出现上面两条已知问题都不算失败。构建脚本以 PDF 是否生成为判据：
latexmk 因交叉引用未稳而以非零码结束是常态，未生成 PDF 才算失败。
