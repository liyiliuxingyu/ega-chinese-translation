#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for i in 1 2; do
  xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_13.4有限点集邻域_校订续译.tex"
done
