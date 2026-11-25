#!/usr/bin/env python3
"""Verify this edition's real inputs, inherited sources, and single-file expansion."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = REPO / "current/EGA_v18"
CHECKS = ROOT / "checks"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def graph(driver):
    paths = []
    def visit(path, stack):
        if path in stack:
            raise ValueError("Recursive TeX input: " + str(path))
        paths.append(path.relative_to(ROOT).as_posix())
        content = path.read_text(encoding="utf-8")
        for name in re.findall(r"\\input\{([^}]+)\}", content):
            child = ROOT / name
            if not child.suffix:
                child = child.with_suffix(".tex")
            if not child.is_file() or ROOT not in child.resolve().parents:
                raise ValueError("Missing or external input: " + name)
            visit(child, stack + (path,))
    visit(ROOT / driver, ())
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-sources", action="store_true",
                        help="Record current source hashes only after explicit integration/diff review.")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("flatten_sources", ROOT / "flatten_sources.py")
    flatten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flatten)
    errors, outputs = [], {}
    all_inputs = set()
    for driver, single in [("main.tex", "single.tex"), ("report.tex", "report_single.tex")]:
        inputs = graph(driver)
        all_inputs.update(inputs)
        duplicates = {p: n for p, n in Counter(inputs).items() if n > 1}
        if duplicates:
            errors.append("duplicate inputs in " + driver + ": " + repr(duplicates))
        expanded = flatten.expand(ROOT / driver)
        actual = (ROOT / single).read_text(encoding="utf-8")
        if actual != expanded:
            errors.append("standalone expansion mismatch: " + single)
        if re.search(r"\\(?:input|include|includegraphics)(?:\[[^\]]*\])?\{", actual):
            errors.append("external input remains in " + single)
        outputs[driver] = {"inputs": inputs, "single": single,
                           "single_sha256": sha(ROOT / single),
                           "matches_expansion": actual == expanded,
                           "duplicate_inputs": duplicates}

    book_inputs = outputs["main.tex"]["inputs"]
    expected_batches = [f"continuations/v18_batch{i:03d}.tex" for i in range(69, 109)]
    for name in expected_batches:
        if book_inputs.count(name) != 1:
            errors.append("new batch not included exactly once: " + name)
    superseded = ["text/v5_01_02.tex", "text/v5_03_06.tex", "continuations/v_dot_early.tex"]
    for name in superseded:
        if name in book_inputs:
            errors.append("superseded overlapping text is still input: " + name)
    revised = ["continuations/" + name for name in ["v19_8_14_18.tex", "v19_8_end.tex", "v19_section9.tex", "v19_section10.tex", "v19_section11.tex"]]
    for name in revised:
        if book_inputs.count(name) != 1:
            errors.append("revised module not included exactly once: " + name)
    if "continuations/v18_first_8_14_onward.tex" in book_inputs:
        errors.append("superseded 8.14-section11 module is still input")
    for name in ["continuations/v_dot_middle.tex", "continuations/v_dot_late.tex"]:
        if book_inputs.count(name) != 1:
            errors.append("inherited later sections missing: " + name)

    preamble = (ROOT / "preamble.tex").read_text(encoding="utf-8")
    if r"\documentclass[UTF8,a4paper]{ctexbook}" not in preamble:
        errors.append("document class changed")
    for command in [r"\setCJKmainfont", r"\setmainfont", r"\setsansfont", r"\geometry{"]:
        if command in preamble:
            errors.append("font or geometry override: " + command)

    # Original edition remains available in the complete repository.  Source-only
    # project ZIPs carry the resulting comparison record for offline continuation.
    preserved, baseline_checked = [], BASE.is_dir()
    if baseline_checked:
        for dirname in ["text", "continuations", "backmatter", "reports"]:
            for path in sorted((BASE / dirname).glob("*.tex")):
                rel = path.relative_to(BASE)
                candidate = ROOT / rel
                if not candidate.is_file() or sha(path) != sha(candidate):
                    errors.append("inherited original file changed: " + rel.as_posix())
                else:
                    preserved.append({"path": rel.as_posix(), "sha256": sha(path)})

    records = [{"path": name, "bytes": (ROOT / name).stat().st_size, "sha256": sha(ROOT / name)}
               for name in sorted(all_inputs)]
    manifest_path = CHECKS / "current_source_inputs.json"
    if args.record_sources:
        if errors:
            raise ValueError("Cannot record a failed source structure: " + repr(errors))
        manifest_path.write_text(json.dumps({"edition": 19, "date": "2026-11-25",
            "scope": "Actual main/report TeX inputs after recorded integration; baseline source comparison is separate.",
            "files": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        expected = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
        if records != expected:
            errors.append("source input manifest differs from recorded edition")

    result = {"pass": not errors, "edition": 19,
              "scope": "Source graph, inherited bytes and standalone expansion; not mathematical proof validation.",
              "source_records": len(records), "new_batch_inputs": len(expected_batches),
              "baseline_checked": baseline_checked, "inherited_original_files_unchanged": preserved,
              "outputs": outputs, "errors": errors}
    (CHECKS / "current_structure_verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": not errors, "source_records": len(records),
                      "new_batch_inputs": len(expected_batches),
                      "inherited_original_files_unchanged": len(preserved),
                      "baseline_checked": baseline_checked, "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
