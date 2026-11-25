#!/usr/bin/env bash
# Source this file from bash. It preserves the document's ctexbook defaults.
ega_project_root="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
command -v xelatex >/dev/null || { echo '需要安装 XeLaTeX。' >&2; return 1; }
if ! kpsewhich ctexbook.cls >/dev/null 2>&1 || ! kpsewhich -engine=xetex xelatex.fmt >/dev/null 2>&1; then
  ega_original_texmf="$(kpsewhich -var-value=TEXMF)"
  ega_original_texmf="${ega_original_texmf//!!/}"
  export TEXMFVAR="$ega_project_root/runtime/texmf-var"
  export TEXMFCONFIG="$ega_project_root/runtime/texmf-config"
  export TEXMF="{$ega_project_root/vendor/texmf,$TEXMFVAR,$ega_original_texmf}"
  mkdir -p "$TEXMFVAR/web2c/xetex" "$TEXMFCONFIG"
  if ! kpsewhich -engine=xetex xelatex.fmt >/dev/null 2>&1; then
    (
      cd "$TEXMFVAR/web2c/xetex"
      xetex -ini -etex -jobname=xelatex -interaction=nonstopmode -halt-on-error xelatex.ini > format-init.stdout.txt 2>&1
    ) || { echo 'XeLaTeX 格式生成失败；详见 runtime/texmf-var/web2c/xetex/format-init.stdout.txt。' >&2; return 1; }
  fi
fi
