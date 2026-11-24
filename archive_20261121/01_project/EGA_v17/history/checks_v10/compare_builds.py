#!/usr/bin/env python3
"""Compare project and standalone builds at text and pixel levels.
Requires PyMuPDF. This is a reproducibility check, not a mathematical review.
"""
from pathlib import Path
import json
import fitz

ROOT = Path(__file__).resolve().parents[1]
def compare(left, right):
    if not left.is_file() or not right.is_file():
        raise FileNotFoundError("First run: bash build.sh --verify-single")
    with fitz.open(left) as a, fitz.open(right) as b:
        assert len(a) == len(b), "Page count differs"
        text_mismatch, pixel_mismatch = [], []
        for i in range(len(a)):
            if a[i].get_text() != b[i].get_text():
                text_mismatch.append(i + 1)
            pa = a[i].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            pb = b[i].get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            if (pa.width, pa.height, pa.n) != (pb.width, pb.height, pb.n) or pa.samples != pb.samples:
                pixel_mismatch.append(i + 1)
        return {"pages_project": len(a), "pages_single": len(b),
                "text_mismatches": text_mismatch, "pixel_mismatches": pixel_mismatch,
                "pixels_checked": len(a)}

if __name__ == "__main__":
    result = {"renderer": "PyMuPDF " + fitz.VersionBind, "raster_dpi": 72,
              "book": compare(ROOT/"main.pdf", ROOT/"single_build/book_single.pdf"),
              "audit": compare(ROOT/"report.pdf", ROOT/"single_build/audit_single.pdf")}
    (ROOT/"checks/build_comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert not result["book"]["text_mismatches"] and not result["book"]["pixel_mismatches"]
    assert not result["audit"]["text_mismatches"] and not result["audit"]["pixel_mismatches"]
