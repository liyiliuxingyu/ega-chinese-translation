#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_线性系与格拉斯曼概形.tex; done
