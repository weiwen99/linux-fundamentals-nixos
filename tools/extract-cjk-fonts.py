#!/usr/bin/env python3
"""从思源宋体集合（TTC）中抽出简体中文 Regular 与 Bold，存成独立 OTF。

为什么需要这一步：nixpkgs 只提供 SourceHanSerif.ttc（163 MB，含五个地区、
七种字重的全部字体），而 XeLaTeX 从集合中按索引取字形时，粗体切换不可靠。
抽出两个单字体文件，排版结果稳定，构建也可复现。

字体许可：SIL Open Font License 1.1（可商用、可嵌入、可再分发）。
仓库不分发字体文件，构建时从 nixpkgs 获取。

用法：
    python3 tools/extract-cjk-fonts.py <SourceHanSerif.ttc> <输出目录>
"""

import sys
from pathlib import Path

TARGETS = {
    "Regular": "SourceHanSerifSC-Regular",
    "Bold": "SourceHanSerifSC-Bold",
}


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    # 延迟导入，避免 --help 时依赖 fontTools。
    from fontTools.ttLib import TTCollection

    collection = TTCollection(str(src), lazy=True)
    written = 0
    for style, postscript in TARGETS.items():
        match = None
        for font in collection.fonts:
            if font["name"].getDebugName(6) == postscript:
                match = font
                break
        if match is None:
            print(f"未找到 {postscript}", file=sys.stderr)
            return 1
        target = out_dir / f"{postscript}.otf"
        match.save(str(target))
        print(f"wrote {target}")
        written += 1
    return 0 if written == len(TARGETS) else 1


if __name__ == "__main__":
    sys.exit(main())
