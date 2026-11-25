# Linux 入门基础：从 NixOS 开始

*Linux Fundamentals: Starting with NixOS*

一本写给完全初学者的 Linux 教材：以 NixOS 作为第一台 Linux，讲命令行、Unix 文化、系统配置、日常开发与服务器运维，最后讲怎么安全地使用 AI Agent。

## 目标读者

没写过程序、没碰过命令行、没装过系统的人。读完应当能够：

- 独立安装 NixOS（虚拟机、实体机、VPS 三条路线）；
- 用命令行完成日常工作，理解 Unix 工具为什么这样设计；
- 读懂并修改 NixOS 配置，升级与回滚；
- 部署并维护一台 Linux 服务器；
- 安装、配置并约束一个 AI Agent。

## 构建

```sh
./build.sh
```

依赖：XeLaTeX（TeX Live 2025+）、`latexminted`/`pygmentize`、`fontTools`、`nix`（取字体）。

在 NixOS 上的一条命令：

```sh
nix shell nixpkgs#texlive.combined.scheme-full nixpkgs#python3Packages.pygments \
          nixpkgs#poppler-utils nixpkgs#source-han-serif --command ./build.sh
```

产物：`build/main.pdf`。

## 目录结构

```
main.tex                 主文件
tex/                     版式、封面、元信息
frontmatter/             前言、阅读指南
chapters/                正文，一章一个文件
tools/                   构建辅助脚本（字体抽取）
docs/                    结构计划、字体与许可说明
build/                   编译产物（不入库）
```

## 许可

- 正文与插图：CC BY-SA 4.0
- 代码示例：MIT

字体许可见 `docs/fonts.md`。
