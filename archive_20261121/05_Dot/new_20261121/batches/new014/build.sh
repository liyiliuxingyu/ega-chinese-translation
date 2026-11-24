#!/bin/sh
set -eu
cd "$(dirname "$0")"
for i in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_特征二与奇异术语_校订续译.tex; done
