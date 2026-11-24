#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for _ in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_153至156_初等奇点局部刻画.tex; done
