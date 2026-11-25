#!/usr/bin/env bash
# 构建《Linux 入门基础：从 NixOS 开始》PDF。
#
# 依赖：XeLaTeX（TeX Live 2025 或更新）、latexminted/pygmentize、fontTools。
# 在 NixOS 上可以直接用：
#   nix shell nixpkgs#texlive.combined.scheme-full nixpkgs#python3Packages.pygments \
#             nixpkgs#poppler-utils nixpkgs#source-han-serif --command ./build.sh
set -euo pipefail

cd "$(dirname "$0")"

FONT_DIR=build/fonts
REGULAR="$FONT_DIR/SourceHanSerifSC-Regular.otf"
BOLD="$FONT_DIR/SourceHanSerifSC-Bold.otf"

if [[ ! -f $REGULAR || ! -f $BOLD ]]; then
  echo "==> 准备中文字体（思源宋体，SIL OFL 1.1）"
  ttc=""
  if command -v nix >/dev/null 2>&1; then
    store_path=$(nix build --no-link --print-out-paths nixpkgs#source-han-serif)
    ttc="$store_path/share/fonts/truetype/SourceHanSerif.ttc"
  fi
  if [[ -z $ttc || ! -f $ttc ]]; then
    echo "找不到 SourceHanSerif.ttc：请先安装 nixpkgs#source-han-serif" >&2
    exit 1
  fi
  python3 tools/extract-cjk-fonts.py "$ttc" "$FONT_DIR"
fi

echo "==> 编译"
latexmk -r latexmkrc main.tex
echo "==> 完成：build/main.pdf"
