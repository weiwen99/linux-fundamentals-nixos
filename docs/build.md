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
   只写 `\allowbreak` 而后面跟空格，会在排版结果里留下一个可见空格。

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

`Overfull \hbox` 应为 0；日志里出现上面那条已知问题不算失败。构建脚本以
PDF 是否生成为判据：latexmk 因交叉引用未稳而以非零码结束是常态，未生成 PDF 才算失败。
