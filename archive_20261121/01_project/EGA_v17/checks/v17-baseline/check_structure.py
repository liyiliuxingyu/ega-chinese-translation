#!/usr/bin/env python3
"""Check source preservation, real input order, and standalone expansion."""
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "checks"
spec = importlib.util.spec_from_file_location("flatten_sources", ROOT / "flatten_sources.py")
flatten = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flatten)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    book = flatten.expand(ROOT / "main.tex")
    report = flatten.expand(ROOT / "report.tex")
    assert book == (ROOT / "single.tex").read_text(encoding="utf-8")
    assert report == (ROOT / "report_single.tex").read_text(encoding="utf-8")
    assert not re.search(r"\\(?:input|include)\{", book + report)
    assert not re.search(r"\\includegraphics(?:\[[^\]]*\])?\{", book + report)
    baseline = json.loads((CHECKS / "baseline_v16_sources.json").read_text())
    allowed = {"text/v1_2.tex", "text/remaining.tex"}
    changed, missing = [], []
    for record in baseline:
        path = ROOT / record["path"]
        if not path.is_file():
            missing.append(record["path"])
        elif sha(path) != record["sha256"]:
            changed.append(record["path"])
    assert not missing, missing
    assert set(changed) == allowed, changed
    old_short = next(x for x in baseline if x["path"] == "text/v1_2.tex")
    assert sha(ROOT / "history/v16_short_before_integration.tex") == old_short["sha256"]
    counters = json.loads((CHECKS / "baseline_v16_counters.json").read_text())
    pattern = {
        "entries": r"\\(?:egap|egas|egapar|egastatement)\{([^}]+)\}",
        "tags": r"\\tag\{([^}]+)\}",
    }
    counts = {}
    for kind, pat in pattern.items():
        previous = Counter(counters[kind])
        current_list = re.findall(pat, book)
        current = Counter(current_list)
        counts[kind] = {
            "baseline": sum(previous.values()),
            "current": len(current_list),
            "missing": dict(previous - current),
            "added": dict(current - previous),
        }
        assert not counts[kind]["missing"], counts[kind]
    driver = (ROOT / "main.tex").read_text()
    additions = [
        "continuations/v_dot_early.tex",
        "continuations/v_dot_middle.tex",
        "continuations/v_dot_late.tex",
    ]
    positions = []
    blocks = {}
    for path in additions:
        needle = r"\input{" + path + "}"
        assert driver.count(needle) == 1, path
        positions.append(driver.index(needle))
        text = (ROOT / path).read_text()
        blocks[path] = {
            "bytes": (ROOT / path).stat().st_size,
            "sha256": sha(ROOT / path),
            "entry_macros": len(re.findall(pattern["entries"], text)),
            "tag_macros": len(re.findall(pattern["tags"], text)),
            "translator_note_macros": len(re.findall(r"\\cmt\{", text)),
            "tikzcd_environments": text.count(r"\begin{tikzcd}"),
        }
    assert positions == sorted(positions)
    joined = "\n".join((ROOT / path).read_text() for path in additions)
    section_headers = re.findall(r"\\egasection\{§(\d+)\\quad", joined)
    assert section_headers == [str(n) for n in range(7, 16)], section_headers
    assert driver.count(r"\input{text/v1_2.tex}") == 1
    result = {
        "pass": True,
        "scope": "File preservation, input structure and macro inventory only; not mathematical proof validation.",
        "baseline_source_records": len(baseline),
        "unchanged_source_records": len(baseline) - len(changed),
        "allowed_changes": changed,
        "missing": missing,
        "old_short_exact_backup": True,
        "standalone_expansions_exact": True,
        "external_tex_or_image_inputs": False,
        "counters": counts,
        "new_body_blocks": blocks,
        "new_section_sequence": section_headers,
        "overlapping_short_input_count": 1,
    }
    (CHECKS / "structure_verification.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
