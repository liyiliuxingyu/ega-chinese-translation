#!/usr/bin/env bash
set -euo pipefail
cd /workspace/scratch/a886fd56dd2f/v23_work/contributions/smoothness
preview_original_texmf="$(kpsewhich -var-value=TEXMF)"
preview_original_texmf="${preview_original_texmf//!!/}"
export TEXMFVAR="$PWD/preview_runtime/texmf-var"
export TEXMFCONFIG="$PWD/preview_runtime/texmf-config"
export TEXMF="{/workspace/scratch/a886fd56dd2f/v23_work/EGA_v23/vendor/texmf,$TEXMFVAR,$preview_original_texmf}"
mkdir -p "$TEXMFVAR/web2c/xetex" "$TEXMFCONFIG"
if ! kpsewhich -engine=xetex xelatex.fmt >/dev/null 2>&1; then
 (cd "$TEXMFVAR/web2c/xetex" && xetex -ini -etex -jobname=xelatex -interaction=nonstopmode -halt-on-error xelatex.ini > format-init.stdout.txt 2>&1)
fi
for doc in preview_body preview_audit; do
 for pass in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error "$doc.tex" > "$doc.pass$pass.stdout" 2>&1
 done
done
