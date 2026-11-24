#!/usr/bin/env python3
"""Validate the current release, independently of historical check directories.

This checks source preservation, real TeX inputs and standalone expansion.
It does not claim to prove mathematical statements.
"""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "checks"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec = importlib.util.spec_from_file_location("flatten_sources", ROOT / "flatten_sources.py")
    flatten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flatten)
    manifest = json.loads((CHECKS / "current_source_inputs.json").read_text(encoding="utf-8"))
    errors = []
    for row in manifest["files"]:
        path = ROOT / row["path"]
        if not path.is_file() or sha(path) != row["sha256"]:
            errors.append("missing or changed source: " + row["path"])

    outputs = {}
    for driver, single in [("main.tex", "single.tex"), ("report.tex", "report_single.tex")]:
        expanded = flatten.expand(ROOT / driver)
        actual = (ROOT / single).read_text(encoding="utf-8")
        if expanded != actual:
            errors.append("standalone expansion mismatch: " + single)
        if re.search(r"\\(?:input|include|includegraphics)(?:\[[^\]]*\])?\{", actual):
            errors.append("unresolved external input: " + single)
        names = re.findall(r"^% BEGIN (.+)$", expanded, flags=re.M)
        duplicate_inputs = {k: v for k, v in Counter(names).items() if v > 1}
        if duplicate_inputs:
            errors.append("duplicate TeX inputs: " + repr(duplicate_inputs))
        outputs[driver] = {
            "single": single,
            "single_sha256": sha(ROOT / single),
            "actual_inputs_in_order": names,
            "duplicate_inputs": duplicate_inputs,
            "standalone_matches": expanded == actual,
        }
    preamble = (ROOT / "preamble.tex").read_text(encoding="utf-8")
    if r"\documentclass[UTF8,a4paper]{ctexbook}" not in preamble:
        errors.append("unexpected document class")
    for command in [r"\setCJKmainfont", r"\setmainfont", r"\setsansfont", r"\geometry{"]:
        if command in preamble:
            errors.append("unexpected font or geometry override: " + command)
    result = {
        "pass": not errors,
        "scope": "File hashes, unique input order and standalone expansion; not mathematical proof validation.",
        "source_records": len(manifest["files"]),
        "outputs": outputs,
        "errors": errors,
    }
    target = CHECKS / "current_structure_verification.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": not errors, "source_records": len(manifest["files"]), "errors": errors}, ensure_ascii=False))
    raise SystemExit(0 if not errors else 1)


if __name__ == "__main__":
    main()
