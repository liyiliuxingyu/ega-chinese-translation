#!/usr/bin/env python3
"""Independent report-only check, writing no shared current/checks results."""
from pathlib import Path
import hashlib
import json
import re
import time
import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent / "ega-recovery/current/EGA_v19"
start = time.monotonic()
paths = ["report.pdf", "single_build/audit_single.pdf", "report.log", "single_build/audit_single.log"]
data = {name: (ROOT / name).read_bytes() for name in paths}
sha = lambda b: hashlib.sha256(b).hexdigest()
needles = ["Overfull", "Underfull", "Missing character", "Undefined control sequence",
           "LaTeX Error", "undefined references", "Font Warning", "Token not allowed"]
fatal = ["Missing character", "Undefined control sequence", "LaTeX Error", "undefined references"]
logs = {}
for name in paths[2:]:
    text = data[name].decode("utf-8", errors="replace")
    row = {key: text.count(key) for key in needles}
    row["sha256"] = sha(data[name])
    row["output_records"] = re.findall(r"Output written on .*", text)
    row["bang_errors"] = re.findall(r"^!.*", text, re.M)
    row["pass_fatal_checks"] = bool(row["output_records"]) and not any(row[k] for k in fatal) and not row["bang_errors"]
    logs[name] = row

diffs = {"text": [], "page_size": [], "pixels": []}
raster_digest = hashlib.sha256()
with fitz.open(stream=data[paths[0]], filetype="pdf") as a, fitz.open(stream=data[paths[1]], filetype="pdf") as b:
    counts = [len(a), len(b)]
    for i in range(min(counts)):
        p,q = a[i],b[i]
        if p.get_text() != q.get_text():
            diffs["text"].append(i+1)
        if p.rect != q.rect:
            diffs["page_size"].append(i+1)
        pr = p.get_pixmap(matrix=fitz.Matrix(1,1), alpha=False)
        qr = q.get_pixmap(matrix=fitz.Matrix(1,1), alpha=False)
        if pr.samples != qr.samples:
            diffs["pixels"].append(i+1)
        raster_digest.update(pr.samples)

stable = {name: (ROOT/name).read_bytes() == data[name] for name in paths}
result = {
    "scope": "Report pair and its two final logs only. No main-PDF claim; writes only this engineering directory.",
    "renderer": "PyMuPDF " + fitz.VersionBind,
    "dpi": 72,
    "input_files": {name: {"bytes": len(data[name]), "sha256": sha(data[name])} for name in paths},
    "logs": logs,
    "pdf_comparison": {"left_pages": counts[0], "right_pages": counts[1], "mismatches": diffs, "left_raster_digest": raster_digest.hexdigest(), "pass": counts[0]==counts[1] and not any(diffs.values())},
    "input_stable_during_check": stable,
    "elapsed_seconds": round(time.monotonic()-start,3),
}
result["pass"] = result["pdf_comparison"]["pass"] and all(row["pass_fatal_checks"] for row in logs.values()) and all(stable.values())
(OUT / "final_report_build_review.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2), flush=True)
raise SystemExit(0 if result["pass"] else 1)
