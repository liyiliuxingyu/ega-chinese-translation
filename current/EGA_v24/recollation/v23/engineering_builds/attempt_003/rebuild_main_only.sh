#!/usr/bin/env bash
set -euo pipefail
source scripts/tex_environment.sh
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" main.tex > "main.pass$pass.log.txt" 2>&1 || {
    tail -60 "main.pass$pass.log.txt"; exit 1;
  }
done
