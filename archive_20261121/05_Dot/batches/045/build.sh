#!/bin/sh
set -eu
cd "$(dirname "$0")"
for i in 1 2; do xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_锥投影微分性质导言_校订续译.tex"; done
