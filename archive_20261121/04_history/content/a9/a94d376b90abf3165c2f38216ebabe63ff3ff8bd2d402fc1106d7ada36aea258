#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v xelatex >/dev/null || { echo '需要安装XeLaTeX及CTeX宏包。' >&2; exit 1; }
source scripts/tex_environment.sh
python3 flatten_sources.py
for f in main report; do
  for pass in 1 2 3; do
    flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
    xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" "$f.tex" > "$f.pass$pass.log.txt" 2>&1 || {
      tail -60 "$f.pass$pass.log.txt"; exit 1;
    }
  done
done
if [[ "${1:-}" == '--verify-single' ]]; then
  mkdir -p single_build
  cp single.tex single_build/book_single.tex
  cp report_single.tex single_build/audit_single.tex
  (
    cd single_build
    for f in book_single audit_single; do
      for pass in 1 2 3; do
        flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
    xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" "$f.tex" > "$f.pass$pass.log.txt" 2>&1 || {
          tail -60 "$f.pass$pass.log.txt"; exit 1;
        }
      done
    done
  )
fi
