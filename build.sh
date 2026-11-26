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

# dist/ 里的 PDF 随仓库提交，供没有 TeX 环境的人直接取用，因此由构建脚本同步。
declare -A DISTNAME=(
  [screen]=linux-fundamentals-nixos-A4-screen.pdf
  [print]=linux-fundamentals-nixos-A4-print.pdf
  [ereader]=linux-fundamentals-nixos-6inch-ereader.pdf
  [phone]=linux-fundamentals-nixos-phone.pdf
)

build_one() {
  local v=$1
  local pdf="build/$v/main-$v.pdf"
  echo "==> 构建版式 $v"
  # minted 需要显式告知输出目录，否则在没有缓存时无法写入 Python 产物。
  mkdir -p "build/$v"
  # 先删旧 PDF：构建失败时若旧文件仍在，会被误判为成功（曾发生一次）。
  rm -f "$pdf"
  export TEXMF_OUTPUT_DIRECTORY="$PWD/build/$v"
  # 首轮常因缺少 .toc/.out 而以非零码结束，判据是 PDF 是否生成；
  # 未生成时再跑一轮，让交叉引用稳定。
  # 单遍限时 15 分钟：出现无限分页时 latexmk 不会自己退出。
  BK_OUT="build/$v" timeout 900 latexmk -f -jobname="main-$v" "variants/$v.tex" >/dev/null 2>&1 || true
  if [[ ! -f $pdf ]]; then
    BK_OUT="build/$v" timeout 900 latexmk -f -jobname="main-$v" "variants/$v.tex" >/dev/null 2>&1 || true
  fi
  if [[ -f $pdf ]]; then
    echo "    $pdf ($(pdfinfo "$pdf" | awk '/Pages/{print $2}') 页)"
    mkdir -p dist
    cp -f "$pdf" "dist/${DISTNAME[$v]}"
    echo "    dist/${DISTNAME[$v]}"
  else
    # 无限分页会污染 .aux 与 .toc（出现过十几 MB 的 aux），后续构建会跟着失败。
    echo "    构建失败：未生成 $pdf（已清理 build/$v）" >&2
    rm -rf "build/$v"
    return 1
  fi
}

case "${1:-all}" in
  # 只删编译中间件。dist/ 里是随仓库提交的发布件，清理不会碰它们。
  clean) rm -rf build; echo "已清理 build/" ;;
  all) for v in "${ALL[@]}"; do build_one "$v"; done ;;
  *) build_one "$1" ;;
esac
