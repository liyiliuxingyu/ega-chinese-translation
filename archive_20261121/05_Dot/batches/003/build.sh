#!/bin/sh
set -eu
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_8.6后预备论证_校订续译.tex
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_8.6后预备论证_校订续译.tex
