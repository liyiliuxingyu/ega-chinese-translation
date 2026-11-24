#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_8.18后线性系讨论_第一批.tex
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_8.18后线性系讨论_第一批.tex
