#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_第8节末域论讨论.tex
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_第8节末域论讨论.tex
