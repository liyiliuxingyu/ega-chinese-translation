#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -f /workspace/shared/tex-env.sh ]; then source /workspace/shared/tex-env.sh; fi
xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_9.4至10.1_校订续译.tex"
xelatex -interaction=nonstopmode -halt-on-error "EGA第五卷_9.4至10.1_校订续译.tex"
