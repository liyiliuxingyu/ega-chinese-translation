#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for _ in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_正交群挠子与局部等平凡性.tex; done
