#!/usr/bin/env bash
set -euo pipefail
source scripts/tex_environment.sh
python3 -B flatten_sources.py
python3 -B checks/verify_current_source.py
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" main.tex > "main.pass$pass.log.txt" 2>&1 || {
    tail -60 "main.pass$pass.log.txt"; exit 1;
  }
done
mkdir -p single_build
cp single.tex single_build/book_single.tex
(
  cd single_build
  for pass in 1 2 3; do
    flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
    xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" book_single.tex > "book_single.pass$pass.log.txt" 2>&1 || {
      tail -60 "book_single.pass$pass.log.txt"; exit 1;
    }
  done
)
