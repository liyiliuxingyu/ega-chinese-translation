#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for n in 1 2; do xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_12节一般截面推广_校订续译.tex"; done
