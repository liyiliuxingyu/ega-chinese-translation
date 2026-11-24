#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for i in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_14.1命题陈述_校订续译.tex"
done
