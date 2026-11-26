#!/usr/bin/env python3
"""Freeze a fully materialized, verified edition-22 overlay without uploading it.

Requires a byte-exact baseline snapshot and finalized local technical records.
Every old payload and old publication-metadata file is read and checked locally.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import zipfile

BASE_COMMIT = "79c1100b13427e447fad5525f27d9b64e4d4ead7"
ROOT_DOCS = ["README.md", "AGENTS.md", "CONTINUE_HERE.md"]
NEW_TOOLS = ["tools/apply_edition22_update.py", "tools/package_edition22.py"]
PROJECT = "current/EGA_v22/"
NEW_METADATA = {".github/workflows/publish-edition22.yml", "EDITION_22_IMPORT.json"}
TEMP_SUFFIXES = {".aux", ".xdv", ".out", ".toc", ".fls", ".fdb_latexmk", ".pyc"}
CHECKS = [
    "current_structure_verification.json", "current_build_log_summary.json",
    "current_pdf_parity.json", "visual_verification_summary.json",
]


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_file(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if (not name or "\\" in name or p.is_absolute() or ".." in p.parts
            or p.as_posix() != name or any(x.lower() == ".git" for x in p.parts)):
        raise ValueError("Unsafe relative path: " + name)
    path = root / name
    if (not path.is_file() or path.is_symlink()
            or any(p.is_symlink() for p in path.parents if p != root)
            or not path.resolve().is_relative_to(root)):
        raise ValueError("Missing or unsafe file: " + name)
    return path


def read_json(root: Path, name: str):
    return json.loads(safe_file(root, name).read_text(encoding="utf-8"))


def baseline_bytes(root: Path, name: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), "show", BASE_COMMIT + ":" + name])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--snapshot-date", required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    day = date.fromisoformat(args.snapshot_date)
    if day.isoformat() != args.snapshot_date:
        raise ValueError("Snapshot date must be canonical YYYY-MM-DD")
    if out.is_relative_to(root):
        raise ValueError("Delivery output must be outside the repository")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("Delivery output directory must be empty")
    stamp = day.strftime("%Y%m%d")
    snapshot = "snapshots/" + stamp + "-v22/"
    project = root / PROJECT

    # No output or root-manifest mutation happens before these actual gates.
    for name in CHECKS:
        data = read_json(project, "checks/" + name)
        if data.get("pass") is not True:
            raise ValueError("Required actual verification has not passed: " + name)
        if data.get("edition") != 22:
            raise ValueError("Old-edition verification cannot authorize this overlay: " + name)
    state = read_json(project, "HANDOVER_STATE.json")
    if (state.get("edition") != 22 or state.get("status") != "build_and_review_verified"
            or state.get("all_books_finished") is not False
            or state.get("base_commit") != BASE_COMMIT
            or state.get("date") != args.snapshot_date
            or state.get("publication", {}).get("release_tag") != "v22-" + stamp):
        raise ValueError("Handover is not accurately finalized for this edition/date")
    artifacts = read_json(project, "ARTIFACTS.json")
    if artifacts.get("edition") != 22 or artifacts.get("status") != "built_and_reviewed":
        raise ValueError("Current artifact record is not finalized edition-22 evidence")
    for name in CHECKS:
        row = artifacts["checks"][name]
        if row.get("pass") is not True or row["sha256"] != sha(safe_file(project, "checks/" + name)):
            raise ValueError("Artifact record does not bind a current verification: " + name)
    for row in artifacts["files"]:
        path = safe_file(project, row["path"])
        if path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError("Final artifact has changed: " + row["path"])

    baseline_path = safe_file(root, snapshot + "REPOSITORY_MANIFEST.json")
    if baseline_path.read_bytes() != baseline_bytes(root, "REPOSITORY_MANIFEST.json"):
        raise ValueError("Snapshot manifest is not the exact pinned baseline manifest")
    old = json.loads(baseline_path.read_text(encoding="utf-8"))
    mapping = {}
    baseline_total = 0
    for row in old["files"]:
        name = row["path"]
        if name in mapping:
            raise ValueError("Duplicate baseline record: " + name)
        candidate_name = snapshot + name if name in ROOT_DOCS else name
        candidate = safe_file(root, candidate_name)
        if candidate.stat().st_size != row["size"] or sha(candidate) != row["sha256"]:
            raise ValueError("Actual baseline bytes mismatch: " + name)
        mapping[name] = row
        baseline_total += row["size"]
    old_metadata = old["allowed_publication_metadata"]
    if not isinstance(old_metadata, list) or len(set(old_metadata)) != len(old_metadata):
        raise ValueError("Invalid prior publication metadata inventory")
    metadata = sorted(set(old_metadata) | NEW_METADATA)
    for name in old_metadata:
        if safe_file(root, name).read_bytes() != baseline_bytes(root, name):
            raise ValueError("Prior publication metadata changed: " + name)

    selected = ROOT_DOCS + NEW_TOOLS
    for prefix in (PROJECT, snapshot):
        directory = root / prefix
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError("Required new payload directory is missing or unsafe: " + prefix)
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlink in new payload: " + str(path))
            if not path.is_file():
                continue
            name = path.relative_to(root).as_posix()
            if "__pycache__" in path.parts or name.startswith(PROJECT + "runtime/"):
                continue
            if path.suffix in TEMP_SUFFIXES or path.name.endswith(".synctex.gz"):
                continue
            selected.append(name)
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate selected payload path")
    for name in selected:
        path = safe_file(root, name)
        if name in mapping and name not in ROOT_DOCS:
            raise ValueError("Attempt to overwrite an old payload: " + name)
        mapping[name] = {"path": name, "size": path.stat().st_size, "sha256": sha(path)}

    # The runner uses strict whole-tree verification: do not silently omit local
    # caches or temporary handoff files that would make the real import fail.
    allowed = set(mapping) | set(metadata) | {"REPOSITORY_MANIFEST.json"}
    extras = []
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        if path.is_file() and rel.as_posix() not in allowed:
            extras.append(rel.as_posix())
    if extras:
        raise ValueError("Move unlisted temporary files outside the repository before freezing: "
                         + json.dumps(extras[:30], ensure_ascii=False)
                         + (" ..." if len(extras) > 30 else ""))

    manifest = {
        "schema_version": 3, "snapshot_date": args.snapshot_date,
        "time_zone": "Asia/Shanghai", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_cutoff": old.get("source_cutoff"),
        "scope": "Preserve every previous engineering payload and all Dot archives; add edition22 "
                 "French/English recollation of first essay section14, explicitly scoped mathematical "
                 "reviews, actual build/visual records and continuation state. All volumes remain unfinished.",
        "baseline_commit": BASE_COMMIT, "baseline_manifest_sha256": sha(baseline_path),
        "allowed_publication_metadata": metadata,
        "files": [mapping[name] for name in sorted(mapping)],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out.mkdir(parents=True, exist_ok=True)
    (root / "REPOSITORY_MANIFEST.json").write_bytes(manifest_bytes)
    selected.append("REPOSITORY_MANIFEST.json")
    expected = {name: mapping[name] for name in selected if name != "REPOSITORY_MANIFEST.json"}
    expected["REPOSITORY_MANIFEST.json"] = {
        "path": "REPOSITORY_MANIFEST.json", "size": len(manifest_bytes),
        "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    archive = out / f"EGA-v22-overlay-{stamp}.zip"
    timestamp = (day.year, day.month, day.day, 0, 0, 0)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for name in sorted(selected):
            path = safe_file(root, name)
            info = zipfile.ZipInfo(name, timestamp)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            with path.open("rb") as source, zipped.open(info, "w", force_zip64=True) as target:
                shutil.copyfileobj(source, target)
    with zipfile.ZipFile(archive) as zipped:
        if (len(zipped.infolist()) != len(selected)
                or set(zipped.namelist()) != set(selected) or zipped.testzip()):
            raise ValueError("Overlay member set or CRC mismatch")
        for info in zipped.infolist():
            row = expected[info.filename]
            with zipped.open(info) as source:
                if (info.file_size != row["size"]
                        or hashlib.file_digest(source, "sha256").hexdigest() != row["sha256"]):
                    raise ValueError("Overlay bytes differ from frozen manifest: " + info.filename)
    parts = []
    rebuilt = hashlib.sha256()
    with archive.open("rb") as source:
        while block := source.read(32 * 1024 * 1024):
            number = len(parts) + 1
            if number > 999:
                raise ValueError("Too many parts for the reviewed workflow interface")
            part = out / (archive.name + f".part{number:03d}")
            part.write_bytes(block)
            rebuilt.update(part.read_bytes())
            parts.append({"file": part.name, "bytes": part.stat().st_size, "sha256": sha(part)})
    if rebuilt.hexdigest() != sha(archive):
        raise ValueError("Ordered-part reconstruction hash mismatch")
    result = {
        "pass": True, "edition": 22, "snapshot_date": args.snapshot_date,
        "release_tag": "v22-" + stamp, "overlay_file": archive.name,
        "baseline_commit": BASE_COMMIT,
        "baseline_payload_files_checked": len(old["files"]),
        "baseline_payload_bytes_checked": baseline_total,
        "baseline_publication_metadata_checked": len(old_metadata),
        "baseline_deferred_to_runner": 0,
        "manifest_payload_records": len(mapping), "overlay_file_count": len(selected),
        "overlay_uncompressed_bytes": sum(row["size"] for row in expected.values()),
        "overlay_zip_bytes": archive.stat().st_size, "overlay_sha256": sha(archive),
        "parts": parts,
        "scope": "Actual full local baseline, frozen manifest members and ordered parts verified. "
                 "No remote mutation or remote publication is performed or inferred.",
    }
    (out / "OVERLAY_VERIFICATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
