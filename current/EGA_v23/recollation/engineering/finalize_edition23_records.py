#!/usr/bin/env python3
"""Record edition-23 artifacts from actual completed checks; never invent reviews.

The integrator first prepares the edition-23 HANDOVER_STATE.json narrative.
This script only fills measured technical fields and ARTIFACTS.json; it does not
write PROGRESS.md or mathematical/source-coverage claims.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

import fitz

BASE_COMMIT = "a1e4d5b58aee845096b7bae25e7e1e7e9482d7fa"
CHECKS = [
    "current_structure_verification.json",
    "current_build_log_summary.json",
    "current_pdf_parity.json",
    "visual_verification_summary.json",
]
LOG_NAMES = ["main", "report", "single_build/book_single", "single_build/audit_single"]


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_file(root: Path, name: str) -> Path:
    rel = PurePosixPath(name)
    if (not name or "\\" in name or rel.is_absolute() or ".." in rel.parts
            or rel.as_posix() != name or ".git" in rel.parts):
        raise ValueError("Unsafe relative file name: " + name)
    path = root / name
    if (not path.is_file() or path.is_symlink()
            or any(p.is_symlink() for p in path.parents if p != root)
            or not path.resolve().is_relative_to(root)):
        raise ValueError("Missing or unsafe regular file: " + name)
    return path


def read_json(root: Path, name: str):
    return json.loads(safe_file(root, name).read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument("--reference-project", type=Path)
    parser.add_argument("--refresh-light-checks", action="store_true",
                        help="Re-run source, final-log and actual-review assembly checks; no new reviews")
    args = parser.parse_args()
    root = args.project.resolve()
    publication_date = date.fromisoformat(args.snapshot_date)
    if publication_date.isoformat() != args.snapshot_date:
        raise ValueError("Snapshot date must be canonical YYYY-MM-DD")
    state = read_json(root, "HANDOVER_STATE.json")
    if (state.get("edition") != 23 or state.get("base_commit") != BASE_COMMIT
            or state.get("base_project") != "current/EGA_v22"
            or state.get("current_project") != "current/EGA_v23"
            or state.get("all_books_finished") is not False):
        raise ValueError("Prepare an accurate edition-23 HANDOVER_STATE.json before finalization")
    for field in ("recollated_this_round", "next"):
        if not isinstance(state.get(field), dict) or not state[field]:
            raise ValueError("Integrator-authored source scope and next position are required: " + field)

    scope = state["recollated_this_round"]
    if (not isinstance(scope.get("range"), str) or not scope["range"].strip()
            or scope.get("status") == "in_progress_not_finalized"):
        raise ValueError("The actual completed recollation range must replace the preparation plan before finalization")

    if args.refresh_light_checks:
        for name in ("verify_current_source.py", "check_build_logs.py",
                     "assemble_visual_verification.py"):
            command = [sys.executable, str(safe_file(root, "checks/" + name))]
            if name == "verify_current_source.py" and args.reference_project:
                command += ["--reference-project", str(args.reference_project.resolve())]
            subprocess.run(command, cwd=root, check=True)
    checks = {}
    data = {}
    for name in CHECKS:
        path = safe_file(root, "checks/" + name)
        data[name] = json.loads(path.read_text(encoding="utf-8"))
        if data[name].get("pass") is not True:
            raise ValueError("Actual required check has not passed: " + name)
        checks[name] = {"pass": True, "sha256": sha(path)}
    structure = data[CHECKS[0]]
    logs = data[CHECKS[1]]
    parity = data[CHECKS[2]]
    visual = data[CHECKS[3]]
    if parity.get("dpi") != 72:
        raise ValueError("The recorded all-page comparison is not the declared 72-dpi check")
    if any(data[name].get("edition") != 23 for name in CHECKS):
        raise ValueError("Inherited prior-edition check records are not edition-23 evidence")
    if (structure.get("baseline_commit") != BASE_COMMIT
            or structure.get("inherited_source_files_unchanged")
            != structure.get("inherited_source_files_expected")
            or structure.get("dot_modules_input_once") != 40
            or structure.get("section15_remainder_byte_identical") is not True
            or structure.get("section14_15_concatenation_matches_original") is not True):
        raise ValueError("Inherited-source or Dot preservation gate failed")

    if {row["name"] for row in logs["logs"]} != set(LOG_NAMES) or len(logs["logs"]) != 4:
        raise ValueError("Expected exactly the four final modular and standalone logs")
    for row in logs["logs"]:
        name = row["name"]
        if (row.get("pass") is not True
                or row["pdf_sha256"] != sha(safe_file(root, name + ".pdf"))
                or row["log_sha256"] != sha(safe_file(root, name + ".log"))
                or row.get("fatal_or_overfull_lines") or row.get("rerun_lines")
                or row["diagnostics"].get("overfull") != 0):
            raise ValueError("Final build evidence no longer matches: " + name)
    for kind in ("main", "report"):
        if visual["final_pdf_sha256"][kind] != sha(safe_file(root, kind + ".pdf")):
            raise ValueError("Actual image reviews do not bind the final PDF: " + kind)
    samples = visual["actual_reviewed_distinct_pages"]
    if (any(not isinstance(samples.get(k), list) or not samples[k] for k in ("main", "report"))
            or sum(len(set(samples[k])) for k in ("main", "report"))
            != visual["actual_reviewed_distinct_page_count"]
            or visual.get("whole_book_human_page_by_page_review") is not False):
        raise ValueError("Invalid or inflated actual visual-review scope")
    pairs = {
        "book_modular_vs_single": ("main.pdf", "single_build/book_single.pdf"),
        "report_modular_vs_single": ("report.pdf", "single_build/audit_single.pdf"),
    }
    for key, (left, right) in pairs.items():
        row = parity["pairs"][key]
        if (row.get("pass") is not True or any(row["mismatches"].values())
                or row["left_sha256"] != sha(safe_file(root, left))
                or row["right_sha256"] != sha(safe_file(root, right))
                or row["left_pages"] != row["right_pages"]):
            raise ValueError("All-page comparison no longer binds the final PDFs: " + key)
    for a, b in (("single.tex", "single_build/book_single.tex"),
                 ("report_single.tex", "single_build/audit_single.tex")):
        if safe_file(root, a).read_bytes() != safe_file(root, b).read_bytes():
            raise ValueError("Standalone compiled source differs from current flattened source: " + a)

    # Bind the actual independent review to the exact five current new sources.
    reviewed = read_json(root, "recollation/v23/FINAL_SOURCE_BINDINGS.json")
    expected_reviewed = set(structure["new_section15_modules"] + structure["new_report_modules"])
    if (reviewed.get("edition") != 23 or reviewed.get("pass") is not True
            or {row["project_relative_path"] for row in reviewed["files"]} != expected_reviewed
            or len(reviewed["files"]) != len(expected_reviewed)
            or reviewed["root_review_sha256"] != sha(safe_file(root, reviewed["root_review_record"]))):
        raise ValueError("Current source-review binding is absent, stale or scoped to different files")
    for row in reviewed["files"]:
        actual = safe_file(root, row["project_relative_path"])
        if actual.stat().st_size != row["bytes"] or sha(actual) != row["sha256"]:
            raise ValueError("A current source differs from its actual reviewed bytes: " + row["project_relative_path"])

    # Capture all active source inputs, rather than hard-coding old file counts.
    active_sources = sorted(set(sum(structure["input_chains"].values(), [])))
    bindings = structure.get("active_source_sha256", {})
    if set(bindings) != set(active_sources):
        raise ValueError("The source check does not bind every active current input")
    for name, expected in bindings.items():
        if sha(safe_file(root, name)) != expected:
            raise ValueError("An active source changed after its structural check: " + name)
    for name in ("single.tex", "report_single.tex"):
        if structure.get("standalone_source_sha256", {}).get(name) != sha(safe_file(root, name)):
            raise ValueError("A standalone source changed after its structural check: " + name)
    paths = [
        "main.pdf", "single.tex", "report.pdf", "report_single.tex",
        "single_build/book_single.tex", "single_build/audit_single.tex",
        "single_build/book_single.pdf", "single_build/audit_single.pdf",
    ] + [name + ".log" for name in LOG_NAMES] + active_sources + [
        "recollation/v23/FINAL_SOURCE_BINDINGS.json", reviewed["root_review_record"]
    ]
    rows = []
    for name in sorted(set(paths)):
        path = safe_file(root, name)
        row = {"path": name, "bytes": path.stat().st_size, "sha256": sha(path)}
        if path.suffix == ".pdf":
            with fitz.open(path) as document:
                row["physical_pages"] = len(document)
        rows.append(row)
    by_name = {row["path"]: row for row in rows}
    for key, (left, right) in pairs.items():
        if (by_name[left]["physical_pages"] != parity["pairs"][key]["left_pages"]
                or by_name[right]["physical_pages"] != parity["pairs"][key]["right_pages"]):
            raise ValueError("Measured PDF page count differs from comparison evidence")
    now = datetime.now(timezone.utc).isoformat()
    artifacts = {
        "edition": 23, "status": "built_and_reviewed", "recorded_at_utc": now,
        "scope": "Actual final local bytes and explicitly scoped technical checks; "
                 "not a claim of full mathematical review or completed remote publication.",
        "files": rows, "checks": checks,
    }
    measured = {
        key: structure[key] for key in (
            "source_records", "inherited_source_files_unchanged",
            "inherited_source_files_expected", "previous_project_actually_read_this_run",
            "previous_project_files_preserved",
            "section13_preserved_original_bytes", "original_v_dot_late_bytes",
            "section14_preserved_original_bytes", "section15_inherited_bytes",
            "section15_remainder_byte_identical", "section14_15_concatenation_matches_original",
            "dot_modules_input_once",
            "current_section15_footnotes",
        )
    }
    measured.update({
        "book_pages": by_name["main.pdf"]["physical_pages"],
        "report_pages": by_name["report.pdf"]["physical_pages"],
        "all_modular_vs_single_pages_text_dimensions_and_72dpi_pixels_equal": True,
        "actual_visual_sample_pages": visual["actual_reviewed_distinct_page_count"],
        "actual_visual_pages": samples,
        "all_pdf_pages_human_reviewed": False,
        "fatal_log_errors": sum(len(row["fatal_or_overfull_lines"]) for row in logs["logs"]),
        "overfull_boxes": sum(row["diagnostics"]["overfull"] for row in logs["logs"]),
        "nonfatal_log_diagnostics": [
            {"name": row["name"], **{k: v for k, v in row["diagnostics"].items()
                                     if k != "all_warning_lines"}}
            for row in logs["logs"]
        ],
        "evidence": "ARTIFACTS.json; checks/current_*.json; checks/visual_verification_summary.json",
    })
    state.update({
        "date": publication_date.isoformat(), "time_zone": "Asia/Shanghai",
        "status": "build_and_review_verified", "technical_checks": measured,
    })
    state["publication"] = {
        "repository": "https://github.com/liyiliuxingyu/ega-chinese-translation",
        "release_tag": "v23-" + publication_date.strftime("%Y%m%d"),
        "record_status": "Frozen before upload. Remote publication must be established by "
                         "EDITION_23_IMPORT.json, the workflow result, the actual remote tag "
                         "and release PACKAGE_VERIFICATION.json; not inferred here.",
    }
    write_json(root / "ARTIFACTS.json", artifacts)
    write_json(root / "HANDOVER_STATE.json", state)
    print(json.dumps({
        "status": state["status"], "artifact_records": len(rows),
        "book_pages": measured["book_pages"], "report_pages": measured["report_pages"],
        "actual_visual_sample_pages": measured["actual_visual_sample_pages"],
        "scope": "Local finalization only; PROGRESS.md and source-coverage narrative were not generated.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
