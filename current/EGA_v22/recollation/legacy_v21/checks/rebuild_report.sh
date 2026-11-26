#!/usr/bin/env bash
# Targeted rebuild after report-only layout corrections; full build.sh remains canonical.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/tex_environment.sh
python3 flatten_sources.py
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" report.tex > "report.pass$pass.log.txt" 2>&1 || {
    tail -60 "report.pass$pass.log.txt"; exit 1;
  }
done
cp report_single.tex single_build/audit_single.tex
cd single_build
for pass in 1 2 3; do
  flags=(); if [[ "$pass" -lt 3 ]]; then flags=(-no-pdf); fi
  xelatex -interaction=nonstopmode -halt-on-error "${flags[@]}" audit_single.tex > "audit_single.pass$pass.log.txt" 2>&1 || {
    tail -60 "audit_single.pass$pass.log.txt"; exit 1;
  }
done
