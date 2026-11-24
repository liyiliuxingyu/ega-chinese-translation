#!/usr/bin/env python3
"""Record the four actual final logs; preserve nonfatal diagnostics."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "checks"
LOGS = ["main.log", "report.log", "single_build/book_single.log", "single_build/audit_single.log"]
NEEDLES = ["Overfull", "Underfull", "Missing character", "Undefined control sequence",
           "LaTeX Error", "undefined references", "Font Warning", "Token not allowed"]
FATAL = ["Missing character", "Undefined control sequence", "LaTeX Error", "undefined references"]
rows = {}
errors = []
(CHECKS / "current_build_logs").mkdir(exist_ok=True)
for name in LOGS:
    path = ROOT / name
    text = path.read_text(encoding="utf-8", errors="replace")
    row = {needle: text.count(needle) for needle in NEEDLES}
    row["output_record"] = re.findall(r"Output written on .*", text)
    row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    row["final_log"] = f"current_build_logs/{path.name}"
    shutil.copy2(path, CHECKS / row["final_log"])
    if not row["output_record"] or any(row[key] for key in FATAL) or re.search(r"^!", text, re.M):
        errors.append(name)
    rows[name] = row
result = {"pass": not errors, "logs": rows, "errors": errors}
(CHECKS / "current_build_log_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(0 if not errors else 1)
