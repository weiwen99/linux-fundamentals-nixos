# 字体与许可

本书的 PDF 会嵌入字体子集。所有字体都开源、可商用、允许嵌入与再分发。

| 用途 | 字体 | 许可 | 来源 |
|---|---|---|---|
| 中文正文 | 思源宋体 SC（Source Han Serif SC） | SIL Open Font License 1.1 | nixpkgs `source-han-serif`（上游 adobe-fonts/source-han-serif 2.003R） |
| 中文标题、界面文字 | 更纱黑体 SC（Sarasa Gothic SC） | SIL Open Font License 1.1 | nixpkgs `sarasa-gothic` |
| 代码（西文与符号） | Recursive Mono Casual（Recursive Mn Csl St） | SIL Open Font License 1.1 | nixpkgs `recursive`（上游 arrowtype/recursive 1.085） |
| 代码（中文注释） | 更纱等宽 SC（Sarasa Fixed SC） | SIL Open Font License 1.1 | nixpkgs `sarasa-gothic` |
| 西文正文 | TeX Gyre Pagella | GUST Font License 1.0 | TeX Live 2025 |

Recursive 的商用许可依据：项目根目录 `OFL.txt` 为标准 SIL OFL 1.1 全文，版权行为「Copyright 2020 The Recursive Project Authors」，其后未声明 Reserved Font Name；字体 `name` 表 ID 13 亦写明 “This Font Software is licensed under the SIL Open Font License, Version 1.1”。OFL 1.1 允许商用、嵌入、修改与再分发，因此可用于本书正文、PDF 嵌入与印刷。

代码块采用静态实例 `RecursiveMonoCslSt-{Regular,Bold,Italic,BdItalic}.otf`，即 CASL 轴取 1（Casual）、MONO 轴取 1（等宽）、wght 取 400 与 700。中文字符回退到更纱等宽 SC，两者字宽不同（Recursive 0.6em，更纱 0.5em），排版时以 `Scale=0.95` 缩小，使每行字符数与旧方案接近。

## 为什么正文用思源宋体

- OFL 1.1 明确允许商用、嵌入、修改与再分发。
- 字形覆盖完整，简繁日韩都在一套字体里，混排标点稳定。
- 有真正的粗体，不必依赖伪粗。

Fandol 系列（TeX Live 自带）是 GPL-3+ 字体例外，也允许商用与嵌入，但上游已标记为过时，本书只把它当作构建回退，交付的 PDF 不使用。

## 构建时怎么取字体

`build.sh` 用 `nix build` 取到 nixpkgs 里 `source-han-serif` 与 `sarasa-gothic` 的路径，把两个目录写进 `build/fonts.tex`；`tex/preamble.tex` 读这个文件，用 `Path=` 加 `FontIndex=` 从字体集合（TTC）里精确取用简体中文的正文、粗体、标题与等宽字面。

这样做的理由：

- 不依赖系统是否装了字体，换一台机器结果一致；
- 不复制字体文件进仓库（集合文件 163 MB，派生文件各约 25 MB）；
- 拿不到 nix 时自动退回按字族名查找，再退回 Fandol 与 Latin Modern，保证没有 Nix 的机器也能编译。

## 许可文本

- SIL OFL 1.1：<https://openfontlicense.org/open-font-license-official-text/>
- GUST Font License：<https://www.gust.org.pl/projects/e-foundry/licenses>
