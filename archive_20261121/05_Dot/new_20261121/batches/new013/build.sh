#!/bin/sh
set -eu
cd "$(dirname "$0")"
for i in 1 2; do xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_光滑塔与分歧概形_校订续译.tex; done
