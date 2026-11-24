#!/usr/bin/env bash
set -euo pipefail
ega_reloc_project=$1
printf 'initial_working_directory=%s\n' "$PWD"
printf 'project=%s\n' "$ega_reloc_project"
source "$ega_reloc_project/scripts/tex_environment.sh"
printf 'resolved_project_root=%s\n' "$ega_project_root"
printf 'TEXMFVAR=%s\n' "${TEXMFVAR:-}"
printf 'TEXMFCONFIG=%s\n' "${TEXMFCONFIG:-}"
printf 'ctexbook=%s\n' "$(kpsewhich ctexbook.cls)"
printf 'xelatex_format=%s\n' "$(kpsewhich -engine=xetex xelatex.fmt)"
printf 'fandol_song=%s\n' "$(kpsewhich FandolSong-Regular.otf)"
cd "$ega_reloc_project"
for pass in 1 2; do
 xelatex -interaction=nonstopmode -halt-on-error -recorder relocation_probe.tex > "relocation_probe.pass${pass}.stdout.txt" 2>&1
done
printf 'probe_compile=success\n'
