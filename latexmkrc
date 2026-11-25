$pdf_mode = 5;
$xelatex = 'xelatex -shell-escape -interaction=nonstopmode -file-line-error %O %S';
$max_repeat = 5;

# 输出目录由构建脚本通过 BK_OUT 指定，默认 build/screen。
$out_dir = $ENV{'BK_OUT'} || 'build/screen';
$aux_dir = $out_dir;
