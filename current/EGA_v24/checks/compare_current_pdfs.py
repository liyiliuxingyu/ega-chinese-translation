#!/usr/bin/env python3
"""Compare every page's text, dimensions and 72-dpi raster with PyMuPDF."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import fitz

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--reference-project", type=Path)
args = parser.parse_args()
pairs = [("book_modular_vs_single", ROOT / "main.pdf", ROOT / "single_build/book_single.pdf"),
         ("report_modular_vs_single", ROOT / "report.pdf", ROOT / "single_build/audit_single.pdf")]
if args.reference_project:
    pairs += [("book_rebuild_vs_received", ROOT / "main.pdf", args.reference_project / "main.pdf"),
              ("report_rebuild_vs_received", ROOT / "report.pdf", args.reference_project / "report.pdf")]
start = time.monotonic()
result = {"edition": 24, "renderer": "PyMuPDF " + fitz.VersionBind, "dpi": 72, "pairs": {}}
all_ok = True
for name, left, right in pairs:
    diffs = {"text": [], "page_size": [], "pixels": []}
    raster_digest = hashlib.sha256()
    with fitz.open(left) as a, fitz.open(right) as b:
        equal_count = len(a) == len(b)
        for i in range(min(len(a), len(b))):
            p, q = a[i], b[i]
            if p.get_text() != q.get_text(): diffs["text"].append(i + 1)
            if p.rect != q.rect: diffs["page_size"].append(i + 1)
            pr = p.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            qr = q.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            pixels = pr.samples
            if pixels != qr.samples: diffs["pixels"].append(i + 1)
            raster_digest.update(pixels)
            if (i + 1) % 200 == 0: print(name, i + 1, "/", len(a), flush=True)
        ok = equal_count and not any(diffs.values())
        all_ok &= ok
        result["pairs"][name] = {
            "pass": ok, "left_pages": len(a), "right_pages": len(b),
            "left_sha256": hashlib.sha256(left.read_bytes()).hexdigest(),
            "right_sha256": hashlib.sha256(right.read_bytes()).hexdigest(),
            "left_raster_digest": raster_digest.hexdigest(), "mismatches": diffs,
        }
result["pass"] = all_ok
result["elapsed_seconds"] = round(time.monotonic() - start, 3)
(ROOT / "checks/current_pdf_parity.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
raise SystemExit(0 if all_ok else 1)
