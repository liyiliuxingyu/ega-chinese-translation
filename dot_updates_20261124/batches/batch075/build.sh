#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_多重射影丛与多次数除子.tex; done
