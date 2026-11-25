# 字体与许可

本书的 PDF 会嵌入字体子集。所有字体都开源、可商用、允许嵌入与再分发。

| 用途 | 字体 | 许可 | 来源 |
|---|---|---|---|
| 中文正文 | 思源宋体 SC（Source Han Serif SC） | SIL Open Font License 1.1 | nixpkgs `source-han-serif`（上游 adobe-fonts/source-han-serif 2.003R） |
| 中文标题、界面文字 | 更纱黑体 SC（Sarasa Gothic SC） | SIL Open Font License 1.1 | nixpkgs `sarasa-gothic` |
| 代码 | 更纱等宽 SC（Sarasa Fixed SC） | SIL Open Font License 1.1 | 同上 |
| 西文正文 | TeX Gyre Pagella | GUST Font License 1.0 | TeX Live 2025 |

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
