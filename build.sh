#!/usr/bin/env bash
# 构建《Linux 入门基础：从 NixOS 开始》的 PDF，四种版式。
#
#   ./build.sh            构建全部版式
#   ./build.sh ereader    只构建一种：screen | print | ereader | phone
#   ./build.sh clean      清理产物
#
# 依赖由 Nix 提供：XeLaTeX（TeX Live 2025，含 ctex/minted/tcolorbox/xltabular）、
# latexminted（随 texlive 提供）、poppler-utils、思源宋体、Sarasa、Recursive。
set -euo pipefail
cd "$(dirname "$0")"

ALL=(screen print ereader phone)

# 首次运行时解析工具与字体路径，写入 build/env.sh，后续复用。
if [[ ! -f build/env.sh ]]; then
  echo "==> 解析构建环境（首次运行需要下载）"
  mkdir -p build
  paths=$(nix build --no-link --print-out-paths \
    'nixpkgs#texlive.combined.scheme-full' \
    'nixpkgs#poppler-utils' \
    'nixpkgs#source-han-serif' \
    'nixpkgs#sarasa-gothic' \
    'nixpkgs#recursive')
  tex=$(echo "$paths" | grep texlive-combined-full | head -1)
  poppler=$(echo "$paths" | grep poppler-utils | head -1)
  shs=$(echo "$paths" | grep source-han-serif | head -1)
  sarasa=$(echo "$paths" | grep sarasa-gothic | head -1)
  recursive=$(echo "$paths" | grep recursive | head -1)
  cat > build/env.sh <<ENV
# 由 build.sh 生成，勿手改。
TEXBIN=$tex/bin
POPPLERBIN=$poppler/bin
SHSDIR=$shs/share/fonts/truetype/
SARASADIR=$sarasa/share/fonts/truetype/
RECURSIVEDIR=$recursive/share/fonts/opentype/
ENV
  cat > build/fonts.tex <<FONTS
% 由 build.sh 生成，勿手改。
\\newcommand{\\shsdir}{$shs/share/fonts/truetype/}
\\newcommand{\\sarasadir}{$sarasa/share/fonts/truetype/}
\\newcommand{\\recursivedir}{$recursive/share/fonts/opentype/}
FONTS
fi

# shellcheck disable=SC1091
source build/env.sh
export PATH="$TEXBIN:$POPPLERBIN:$PATH"

build_one() {
  local v=$1
  local pdf="build/$v/main-$v.pdf"
  echo "==> 构建版式 $v"
  # 首轮常因缺少 .toc/.out 而以非零码结束，判据是 PDF 是否生成；
  # 未生成时再跑一轮，让交叉引用稳定。
  BK_OUT="build/$v" latexmk -f -jobname="main-$v" "variants/$v.tex" >/dev/null 2>&1 || true
  if [[ ! -f $pdf ]]; then
    BK_OUT="build/$v" latexmk -f -jobname="main-$v" "variants/$v.tex" >/dev/null 2>&1 || true
  fi
  if [[ -f $pdf ]]; then
    echo "    $pdf ($(pdfinfo "$pdf" | awk '/Pages/{print $2}') 页)"
  else
    echo "    构建失败：未生成 $pdf" >&2
    return 1
  fi
}

case "${1:-all}" in
  clean) rm -rf build dist/*.pdf; echo "已清理" ;;
  all) for v in "${ALL[@]}"; do build_one "$v"; done ;;
  *) build_one "$1" ;;
esac
