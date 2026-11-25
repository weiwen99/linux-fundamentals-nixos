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

## 构建时怎么得到字体

`nixpkgs` 只提供 `SourceHanSerif.ttc` 这一个 163 MB 的集合文件，含五个地区、七种字重。XeLaTeX 直接从集合里按索引切换粗体并不可靠，因此 `tools/extract-cjk-fonts.py` 从集合中抽出简体中文的 Regular 与 Bold 两个单字体文件，写到 `build/fonts/`。

字体文件不进仓库：

- 体积大（各约 25 MB）；
- 许可要求再分发时附带许可文本，直接从 nixpkgs 取更干净；
- 构建可复现，`build.sh` 会按需生成。

## 许可文本

- SIL OFL 1.1：<https://openfontlicense.org/open-font-license-official-text/>
- GUST Font License：<https://www.gust.org.pl/projects/e-foundry/licenses>
