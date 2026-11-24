#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_法文覆盖审计_泛截面光滑性.tex; done
