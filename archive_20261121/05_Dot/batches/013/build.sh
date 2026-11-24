#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_9.1至9.2_校订续译.tex
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_9.1至9.2_校订续译.tex
