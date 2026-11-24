#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/01_project/EGA_v17"
bash build.sh --verify-single
python3 checks/check_current_build_logs.py
python3 checks/compare_current_pdfs.py
printf '%s\n' '构建与逐页比对已完成。请核查实际内容、页图和当前状态，再更新交付清单；不要把旧状态自动当作本次完成度。'
