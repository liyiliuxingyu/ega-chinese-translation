#!/bin/sh
set -eu
cd "$(dirname "$0")"
for i in 1 2; do xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_平坦性假设与非空性公理_校订续译.tex"; done
