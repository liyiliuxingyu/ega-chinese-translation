#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for pass in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_射影丛的Picard群与零次态射.tex; done
