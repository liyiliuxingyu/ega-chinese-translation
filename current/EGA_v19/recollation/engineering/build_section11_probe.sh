#!/usr/bin/env bash
set -euo pipefail
section11_work_root="/workspace/scratch/a886fd56dd2f/edition19_work/engineering"
section11_vendor="/workspace/scratch/a886fd56dd2f/ega-recovery/current/EGA_v19/vendor/texmf"
section11_original_texmf="$(kpsewhich -var-value=TEXMF)"
section11_original_texmf="${section11_original_texmf//!!/}"
export TEXMFVAR="$section11_work_root/texmf-var"
export TEXMFCONFIG="$section11_work_root/texmf-config"
export TEXMF="{$section11_vendor,$TEXMFVAR,$section11_original_texmf}"
mkdir -p "$TEXMFVAR/web2c/xetex" "$TEXMFCONFIG" "$section11_work_root/section11_probe_build"
if ! kpsewhich -engine=xetex xelatex.fmt >/dev/null 2>&1; then
  (
    cd "$TEXMFVAR/web2c/xetex"
    xetex -ini -etex -jobname=xelatex -interaction=nonstopmode -halt-on-error xelatex.ini > format-init.stdout.txt 2>&1
  )
fi
cd "$section11_work_root"
for section11_pass in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error -output-directory=section11_probe_build section11_probe.tex > "section11_probe_build/pass${section11_pass}.stdout.txt" 2>&1
done
