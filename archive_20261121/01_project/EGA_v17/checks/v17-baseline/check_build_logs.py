#!/usr/bin/env python3
"""Record final build warnings without concealing nonfatal diagnostics."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "checks"
NAMES = ("main.log", "report.log", "single_build/book_single.log",
         "single_build/audit_single.log")
NEEDLES = ("Overfull", "Underfull", "Missing character",
           "Undefined control sequence", "LaTeX Error",
           "undefined references", "Font Warning", "Token not allowed")
FATAL = ("Overfull", "Missing character", "Undefined control sequence",
         "LaTeX Error", "undefined references")
out = {}
(CHECKS / "build_logs").mkdir(exist_ok=True)
for name in NAMES:
    path = ROOT / name
    text = path.read_text(errors="replace")
    row = {needle: text.count(needle) for needle in NEEDLES}
    row["output_record"] = re.findall(r"Output written on .*", text)
    row["log_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert row["output_record"], name
    assert not any(row[key] for key in FATAL), (name, row)
    assert not re.search(r"^!", text, re.M), name
    shutil.copy2(path, CHECKS / "build_logs" / path.name)
    out[name] = row
(CHECKS / "build_log_summary.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(out, ensure_ascii=False, indent=2))
