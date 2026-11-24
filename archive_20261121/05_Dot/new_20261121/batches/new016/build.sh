#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for _ in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_151光滑型与雅可比判据_校订续译.tex; done
