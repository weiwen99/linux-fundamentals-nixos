# Linux 入门基础：从 NixOS 开始

*Linux Fundamentals: Starting with NixOS*

一本写给完全初学者的 Linux 教材：以 NixOS 作为第一台 Linux，讲命令行、Unix 传统、系统配置、日常开发与服务器运维，最后讲怎么安全地使用 AI Agent。

全书 36 章，分五部分：起步、系统、开发、运维、Agent。

## 下载

不需要安装 TeX，四种版式的 PDF 都已放进仓库：

| 文件 | 纸张与字号 | 页数 |
|---|---|---|
| [`dist/linux-fundamentals-nixos-A4-screen.pdf`](dist/linux-fundamentals-nixos-A4-screen.pdf) | A4，11pt，彩色 | 205 |
| [`dist/linux-fundamentals-nixos-A4-print.pdf`](dist/linux-fundamentals-nixos-A4-print.pdf) | A4，11pt，双面装订 | 211 |
| [`dist/linux-fundamentals-nixos-6inch-ereader.pdf`](dist/linux-fundamentals-nixos-6inch-ereader.pdf) | 91 × 122 mm，9pt，灰度 | 394 |
| [`dist/linux-fundamentals-nixos-phone.pdf`](dist/linux-fundamentals-nixos-phone.pdf) | 88 × 176 mm，9pt，彩色 | 278 |

页数随版本变化，以文件为准。每个版本的 PDF 也附在
[Releases](https://github.com/weiwen99/linux-fundamentals-nixos/releases) 里，
另有源码标签可对照。

## 目标读者

没写过程序、没碰过命令行、没装过系统的人。读完应当能够：

- 独立安装 NixOS（虚拟机、实体机、VPS 三条路线）；
- 用命令行完成日常工作，理解 Unix 工具为什么这样设计；
- 读懂并修改 NixOS 配置，升级与回滚；
- 部署并维护一台 Linux 服务器；
- 安装、配置并约束一个 AI Agent。

## 四种版式

同一份源文件编译出四种版式，内容一致，纸张、字号、页边距与配色不同。

| 版式 | 纸张与字号 | 用途 | 特点 |
|---|---|---|---|
| `screen` | A4，11pt | 电脑屏幕阅读 | 默认版式，彩色插图 |
| `print` | A4，11pt | 印刷装订 | 内侧加宽装订线，双面排版 |
| `ereader` | 91 × 122 mm，9pt | 6 寸电子墨水阅读器 | 灰度配色，窄边距 |
| `phone` | 88 × 176 mm，9pt | 手机竖屏 | 彩色配色，页面更高 |

窄版式下若干宽幅示意图会换成等价的表格，避免缩到不可读；时间线一节即为一例。

## 构建

```sh
./build.sh            # 四种版式全部构建
./build.sh ereader    # 只构建一种：screen | print | ereader | phone
./build.sh clean      # 清理产物
```

依赖由 Nix 提供：XeLaTeX（TeX Live 2025，含 `ctex`、`minted`、`tcolorbox`、
`xltabular`、`adjustbox`、`float`）、`poppler-utils`、思源宋体、Sarasa、Recursive。

首次运行 `build.sh` 会执行一次 `nix build` 解析工具与字体路径，写入 `build/env.sh`
与 `build/fonts.tex`，之后复用。命令行二进制来自 Nix store，因此系统级不必安装 TeX。

产物：`build/<版式>/main-<版式>.pdf`，同时同步到 `dist/` 下的发布文件名。

## 目录结构

```
main.tex                 主文件（章节顺序、分部）
tex/
  meta.tex               书名、作者、版本
  layout.tex             版式参数（screen / print / ereader / phone）
  preamble.tex           页面、字体、颜色、标题、代码、提示框
  cover.tex              封面
variants/                四种版式的包装文件，只负责 \def\booklayout{...}
frontmatter/             前言、阅读指南
chapters/                正文，一章一个文件
docs/
  outline.md             章节计划与已核实的版本事实
  style.md               文风规范
  fonts.md               字体与许可说明
build/                   编译中间件（不入库）
dist/                    四种版式的 PDF（入库，供直接下载）
```

## 许可

- 正文与插图：CC BY-SA 4.0，全文见 `LICENSE`
- 代码示例与 `build.sh`：MIT，全文见 `LICENSE-CODE`

字体许可见 `docs/fonts.md`：思源宋体、Sarasa、Recursive 均为 SIL OFL 1.1，
TeX Gyre Pagella 为 GUST Font License，四者都允许商用与嵌入。
