#!/usr/bin/env bash
# 构建《Linux 入门基础：从 NixOS 开始》PDF。
#
# 依赖：XeLaTeX（TeX Live 2025+，含 ctex/minted/tcolorbox）、latexminted 或
# pygmentize、nix（用于取中文字体）。
#
# NixOS 上：
#   nix shell nixpkgs#texlive.combined.scheme-full nixpkgs#source-han-serif \
#             nixpkgs#sarasa-gothic --command ./build.sh
set -euo pipefail

cd "$(dirname "$0")"

# 把 nixpkgs 里的字体路径写进 build/fonts.tex，供 preamble.tex 按 FontIndex 取字面。
# 拿不到 nix 时跳过，preamble 会退回按字族名查找。
write_font_paths() {
  if ! command -v nix >/dev/null 2>&1; then
    echo "==> 未找到 nix，跳过字体路径生成（改用系统字体）"
    return
  fi

  echo "==> 解析字体路径"
  local shs sarasa recursive
  shs=$(nix build --no-link --print-out-paths nixpkgs#source-han-serif)/share/fonts/truetype/
  sarasa=$(nix build --no-link --print-out-paths nixpkgs#sarasa-gothic)/share/fonts/truetype/
  recursive=$(nix build --no-link --print-out-paths nixpkgs#recursive)/share/fonts/opentype/

  mkdir -p build
  cat > build/fonts.tex <<FONTS
% 由 build.sh 生成，勿手改。
\\newcommand{\\shsdir}{$shs}
\\newcommand{\\sarasadir}{$sarasa}
\\newcommand{\\recursivedir}{$recursive}
FONTS
  echo "    思源宋体：$shs"
  echo "    Sarasa：  $sarasa"
  echo "    Recursive：$recursive"
}

write_font_paths

echo "==> 编译"
latexmk -r latexmkrc main.tex

echo "==> 完成：build/main.pdf"
