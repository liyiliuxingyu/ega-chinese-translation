#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for _ in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_161至163_光滑二次型.tex; done
