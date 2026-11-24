#!/bin/sh
set -eu
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_第7节_独立续译.tex
xelatex -interaction=nonstopmode -halt-on-error EGA第五卷_第7节_独立续译.tex
