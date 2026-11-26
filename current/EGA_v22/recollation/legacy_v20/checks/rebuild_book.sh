#!/usr/bin/env bash
# Targeted rebuild after book footnote anchor corrections; full build.sh remains canonical.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/tex_environment.sh
python3 flatten_sources.py
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" main.tex > "main.pass$pass.log.txt" 2>&1 || {
    tail -60 "main.pass$pass.log.txt"; exit 1;
  }
done
cp single.tex single_build/book_single.tex
cd single_build
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" book_single.tex > "book_single.pass$pass.log.txt" 2>&1 || {
    tail -60 "book_single.pass$pass.log.txt"; exit 1;
  }
done
