#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source scripts/tex_environment.sh
python3 flatten_book.py
mkdir -p build
for pass in 1 2 3; do
 opts=(); if [[ $pass -lt 3 ]]; then opts=(-no-pdf); fi
 xelatex -interaction=nonstopmode -halt-on-error -output-directory=build "${opts[@]}" main.tex > "build/main.pass$pass.txt" 2>&1 || { tail -70 "build/main.pass$pass.txt"; exit 1; }
done
