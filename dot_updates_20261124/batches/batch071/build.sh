#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for _ in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_定理16.9_光滑二次型的判据.tex; done
