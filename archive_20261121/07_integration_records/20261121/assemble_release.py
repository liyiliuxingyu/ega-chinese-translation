#!/usr/bin/env python3
"""Assemble a readable current project plus losslessly deduplicated history.

Input roots and archived ZIP member lists refer to this recovery session.
The delivered restore/verify tools, rather than this staging recipe, are the
portable user entry points. Nothing in the recovered inputs is modified.
"""
from pathlib import Path, PurePosixPath
import csv
import hashlib
import json
import shutil
import zipfile
import fitz

WORKSPACE = Path(__file__).resolve().parents[1]
OUT = WORKSPACE / "release_20261121/EGA_20261121_Dot_handover"
WORK = WORKSPACE / "work_20261121/project"
INTEGRATION = WORKSPACE / "integration_20261121"
VERSIONS = {
    "v17": {
        "root_name": "EGA_v17_handover",
        "root": WORKSPACE / "restored_20261121/baseline/EGA_v17_handover",
        "zip": WORKSPACE / "recovered_20261121/baseline/EGA中文译校_第十七版_完整续作工程包.zip",
    },
    "supplement_III": {
        "root_name": "EGA_v17_V_supplement_III",
        "root": WORKSPACE / "restored_20261121/latest/EGA_v17_V_supplement_III",
        "zip": WORKSPACE / "recovered_20261121/latest/EGA中文译校_第十七版_第五卷增补第三辑_完整续作工程.zip",
    },
    "supplement_III_delta": {
        "root_name": "EGA_v17_V_supplement_III_delta",
        "root": WORKSPACE / "restored_20261121/delta3/EGA_v17_V_supplement_III_delta",
        "zip": WORKSPACE / "recovered_20261121/latest/EGA中文译校_第十七版_第五卷增补第三辑_增量包.zip",
    },
}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(relative, value):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy(source, relative):
    relative = PurePosixPath(relative)
    assert not relative.is_absolute() and ".." not in relative.parts
    assert source.is_file() and not source.is_symlink(), source
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert sha(source) == sha(target), target
    else:
        shutil.copy2(source, target)
    return target


def original_members(version):
    prefix = version["root_name"] + "/"
    with zipfile.ZipFile(version["zip"]) as z:
        members = []
        for info in z.infolist():
            if info.is_dir():
                continue
            assert info.filename.startswith(prefix), info.filename
            relative = info.filename[len(prefix):]
            p = PurePosixPath(relative)
            assert relative and not p.is_absolute() and ".." not in p.parts
            source = version["root"] / relative
            assert source.is_file() and source.stat().st_size == info.file_size, relative
            members.append((relative, source))
        return members


def main():
    if OUT.exists():
        raise RuntimeError("Output already exists; do not overwrite an assembled package.")
    OUT.mkdir(parents=True)
    manifests = {key: original_members(value) for key, value in VERSIONS.items()}

    # Keep the actual current engineering tree readable; do not package runtime,
    # caches, XDV, AUX, TOC and other reproducible temporary build files.
    active_count = 0
    for relative, _ in manifests["supplement_III"]:
        if not relative.startswith("project/"):
            continue
        project_relative = relative[len("project/"):]
        source = WORK / project_relative
        if source.is_file():
            copy(source, "01_project/EGA_v17/" + project_relative)
            active_count += 1
    extras = [
        "checks/check_current_project.py", "checks/check_current_build_logs.py",
        "checks/compare_current_pdfs.py", "checks/VISUAL_REVIEW_20261121.md",
        "checks/visual_review_20261121.json",
    ]
    extras += [p.relative_to(WORK).as_posix() for p in (WORK / "checks").glob("current_*") if p.is_file()]
    for directory in ["checks/current_build_logs", "checks/current_build_passes", "history/handover_received_supplement_III"]:
        extras += [p.relative_to(WORK).as_posix() for p in (WORK / directory).rglob("*") if p.is_file()]
    extras += ["single_build/book_single.pdf", "single_build/audit_single.pdf",
               "single_build/book_single.log", "single_build/audit_single.log", "main.log", "report.log"]
    for relative in sorted(set(extras)):
        copy(WORK / relative, "01_project/EGA_v17/" + relative)

    for relative, source in manifests["supplement_III"]:
        if relative.startswith("03_sources/"):
            copy(source, relative)
    for relative, source in manifests["v17"]:
        if relative.startswith("05_Dot/"):
            copy(source, relative)

    # Every new original ZIP is retained, while its text/code/metadata members
    # are also available directly in an isolated per-batch directory.
    audit = json.loads((INTEGRATION / "dot_new_audit.json").read_text(encoding="utf-8"))
    records = audit["records"]
    for row in records:
        archive = WORKSPACE / row["local_archive_path"]
        assert sha(archive) == row["zip_sha256"]
        archive_relative = "05_Dot/new_20261121/original_archives/" + row["archive_name"]
        copy(archive, archive_relative)
        batch_root = OUT / "05_Dot/new_20261121/batches" / row["id"]
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                if item.is_dir() or Path(item.filename).suffix.lower() == ".pdf":
                    continue
                rel = PurePosixPath(item.filename)
                assert not rel.is_absolute() and ".." not in rel.parts
                target = batch_root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(z.read(item))
        source_path = batch_root / row["main_tex_entry"]
        assert sha(source_path) == row["source_tex_sha256"]
    for relative, source in manifests["supplement_III"]:
        if relative.startswith("05_Dot_new_batches/") and source.suffix == ".json":
            copy(source, "05_Dot/new_20261121/provenance/" + source.name)

    combined = json.loads((INTEGRATION / "dot_combined_index.json").read_text(encoding="utf-8"))
    for row in combined["records"]:
        row["integration_status"] = "included_in_current_source; mathematical review remains separately qualified"
        row["current_project_input"] = "01_project/EGA_v17/" + row["merged_target_file"]
        if row["id"].startswith("old"):
            row["packaged_source_path"] = row["existing_package_relative_source_path"]
        else:
            row["packaged_archive_path"] = "05_Dot/new_20261121/original_archives/" + row["archive_name"]
            row["packaged_source_path"] = "05_Dot/new_20261121/batches/" + row["id"] + "/" + row["main_tex_entry"]
            for key in ["suggested_archive_relative_path", "suggested_source_relative_path", "suggested_paths_status"]:
                row.pop(key, None)
        assert sha(OUT / row["packaged_source_path"]) == row["source_tex_sha256"]
        assert (OUT / row["current_project_input"]).is_file()
    combined["packaged_source_paths_verified"] = True
    combined["current_package_revision"] = "20261121-dot-consolidation"
    write_json("05_Dot/DOT_BATCHES_COMBINED.json", combined)
    with (OUT / "05_Dot/DOT_BATCHES_COMBINED.tsv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["stable_id", "original_label", "source_tex_sha256", "source_path", "project_input", "treatment"])
        for row in combined["records"]:
            writer.writerow([row["id"], row["source_label"], row["source_tex_sha256"], row["packaged_source_path"], row["current_project_input"], row["integration_treatment"]])

    # Copy audit evidence selectively. Private transfer requests and unrelated
    # Library search results are deliberately not part of the engineering pack.
    selected = [
        "baseline_audit.json", "baseline_audit.md", "baseline_extraction.json",
        "baseline_all_1827_path_mapping.json", "baseline_mapping_validation.json",
        "v16_435_mapping_reverified.json", "byte_identical_duplicates.json",
        "proposed_merge_inventory.json", "dedup_candidates_preserve_active_project.json",
        "run_baseline_audit.py", "latest_project_audit.json", "latest_project_audit.md",
        "dot_new_audit.json", "dot_new_audit.md", "dot_new_index.json", "dot_new_index.tsv",
        "dot_combined_index.json", "library_sources.json", "recovered_latest_archives.json",
    ]
    for relative in selected:
        source = INTEGRATION / relative
        if source.is_file():
            copy(source, "07_integration_records/20261121/" + relative)
    for directory in ["visual_review", "latest_audit_evidence"]:
        for source in sorted((INTEGRATION / directory).rglob("*")):
            if source.is_file():
                copy(source, "07_integration_records/20261121/" + source.relative_to(INTEGRATION).as_posix())
    for name in ["archive_inventory.json", "source_pdf_identity.json", "finalize_audit.py"]:
        source = INTEGRATION / "dot_audit_extract" / name
        if source.is_file():
            copy(source, "07_integration_records/20261121/dot_audit_extract/" + name)

    corpus = []
    for source in sorted((OUT / "03_sources").iterdir()):
        row = {"path": source.relative_to(OUT).as_posix(), "bytes": source.stat().st_size, "sha256": sha(source)}
        if source.suffix.lower() == ".pdf":
            with fitz.open(source) as doc:
                row["physical_pages"] = len(doc)
        else:
            row["format"] = "PostScript; original bytes preserved"
        corpus.append(row)
    assert len(corpus) == 13
    write_json("07_integration_records/20261121/source_corpus_manifest.json", {"files": corpus})

    # Restore maps refer to physical existing files. Only otherwise absent
    # historical bytes become content-addressed objects. No symlink/hardlink or
    # prerequisite external base archive is needed by a future conversation.
    by_sha = {}
    for source in sorted(OUT.rglob("*")):
        if source.is_file():
            by_sha.setdefault(sha(source), source.relative_to(OUT).as_posix())
    restore = {"schema_version": 1, "scope": "Exact paths and bytes of all regular files in the three recovered archives; does not recreate original ZIP container bytes.", "versions": {}}
    archive_summary = []
    stored_new_objects = 0
    for key, info in VERSIONS.items():
        archive = {"file_name": info["zip"].name, "bytes": info["zip"].stat().st_size, "sha256": sha(info["zip"])}
        rows = []
        for original_path, source in manifests[key]:
            digest = sha(source)
            if digest not in by_sha:
                stored = f"04_history/content/{digest[:2]}/{digest}"
                copy(source, stored)
                by_sha[digest] = stored
                stored_new_objects += 1
            stored = by_sha[digest]
            assert (OUT / stored).stat().st_size == source.stat().st_size
            rows.append({"original_path": original_path, "stored_path": stored, "bytes": source.stat().st_size, "sha256": digest})
        restore["versions"][key] = {"root_name": info["root_name"], "archive": archive, "files": rows}
        archive_summary.append({"version": key, **archive, "ordinary_files_preserved": len(rows)})
    write_json("04_history/RESTORE_INDEX.json", restore)
    write_json("07_integration_records/20261121/RECOVERED_PACKAGES.json", {"archives": archive_summary})
    summary = {"current_project_original_positions_retained": active_count, "source_corpus_count": len(corpus), "dot_source_batches": len(combined["records"]), "additional_historical_content_objects": stored_new_objects,
               "restorable_versions": {key: len(v["files"]) for key, v in restore["versions"].items()},
               "ordinary_files_at_assembly": sum(p.is_file() for p in OUT.rglob("*"))}
    write_json("07_integration_records/20261121/assembly_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
