#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_除子族的固定点与转置.tex; done
