#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source scripts/tex_environment.sh
python3 flatten_sources.py
for job in main single report report_single; do
  dir=build_III/"$job"; mkdir -p "$dir"
  for pass in 1 2 3; do
    opt=()
    if ((pass<3)); then opt=(-no-pdf); fi
    xelatex -interaction=nonstopmode -halt-on-error -output-directory="$dir" "${opt[@]}" "$job.tex" > "$dir/pass$pass.stdout.txt" 2>&1 ||
      { tail -80 "$dir/pass$pass.stdout.txt"; exit 1; }
  done
done

