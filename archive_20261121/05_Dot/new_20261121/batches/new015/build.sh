#!/bin/sh
set -eu
cd "$(dirname "$0")"
for i in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_切超曲面与勘误_校订续译.tex; done
