#!/usr/bin/env python3
"""Package the verified current project and, optionally, the whole EGA/Dot repository."""
from pathlib import Path, PurePosixPath
from datetime import date
import argparse
import hashlib
import json
import shutil
import stat
import zipfile

PUBLICATION_METADATA = {'.github/workflows/import-20261124.yml', '.github/workflows/publish-archive-supplement-20261125.yml', '.github/workflows/publish-edition18.yml', '.github/workflows/publish-edition19.yml', '.github/workflows/publish-edition20.yml', '.github/workflows/publish-edition21.yml', '.github/workflows/publish-edition22.yml', '.github/workflows/publish-edition23.yml', '.github/workflows/publish-edition24.yml', 'ARCHIVE_SUPPLEMENT_IMPORT.json', 'EDITION_18_IMPORT.json', 'EDITION_19_IMPORT.json', 'EDITION_20_IMPORT.json', 'EDITION_21_IMPORT.json', 'EDITION_22_IMPORT.json', 'EDITION_23_IMPORT.json', 'EDITION_24_IMPORT.json', 'IMPORT_RECEIPT.json'}


def safe_name(name):
    p = PurePosixPath(name)
    return (bool(name) and "\\" not in name and p.as_posix() == name
            and not p.is_absolute() and ".." not in p.parts
            and all(x.lower() != ".git" for x in p.parts))


def safe_file(root, name):
    if not safe_name(name):
        raise ValueError("Unsafe manifest path: " + name)
    path = root / name
    if (path.is_symlink() or not path.is_file()
            or any(x.is_symlink() for x in path.parents if x != root)
            or not path.resolve().is_relative_to(root)):
        raise ValueError("Not a safe regular repository file: " + name)
    return path


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pack(root, names, target, strip_prefix="", *, timestamp):
    records = []
    if len(set(names)) != len(names):
        raise ValueError("Duplicate package paths")
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9,
                         allowZip64=True) as archive:
        for name in sorted(names):
            path = safe_file(root, name)
            if strip_prefix and not name.startswith(strip_prefix):
                raise ValueError("Project file outside the expected prefix")
            arcname = name.removeprefix(strip_prefix) if strip_prefix else name
            if strip_prefix:
                arcname = "EGA_v24/" + arcname
            if not safe_name(arcname):
                raise ValueError("Unsafe ZIP member name")
            info = zipfile.ZipInfo(arcname, timestamp)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            with path.open("rb") as source, archive.open(info, "w", force_zip64=True) as dest:
                shutil.copyfileobj(source, dest)
            records.append({"path": arcname, "size": path.stat().st_size, "sha256": sha(path)})
    # Re-read every entry rather than trusting a successful ZIP close.
    with zipfile.ZipFile(target) as archive:
        if set(archive.namelist()) != {r["path"] for r in records}:
            raise ValueError("ZIP path mismatch")
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC mismatch")
        for row in records:
            info = archive.getinfo(row["path"])
            with archive.open(info) as source:
                if info.file_size != row["size"] or hashlib.file_digest(source, "sha256").hexdigest() != row["sha256"]:
                    raise ValueError("ZIP byte mismatch: " + row["path"])
    return {"file": target.name, "size": target.stat().st_size, "sha256": sha(target),
            "members": len(records), "uncompressed_bytes": sum(x["size"] for x in records),
            "all_member_hashes_verified": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.is_relative_to(root):
        raise ValueError("Package output must be outside the frozen repository")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Output directory must be empty")
    manifest = json.loads((root / "REPOSITORY_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("baseline_commit") != "aaa56a394186471c071e9d9cc686401becadf98e":
        raise ValueError("The manifest is not the frozen edition24 baseline transition")
    publication_date = date.fromisoformat(manifest["snapshot_date"])
    if publication_date.isoformat() != manifest["snapshot_date"]:
        raise ValueError("Non-canonical publication date")
    stamp = publication_date.strftime("%Y%m%d")
    timestamp = (publication_date.year, publication_date.month, publication_date.day, 0, 0, 0)
    records = manifest["files"]
    names = [x["path"] for x in records]
    if len(set(names)) != len(names) or "REPOSITORY_MANIFEST.json" in names:
        raise ValueError("Duplicate or self-referential manifest entry")
    for row in records:
        path = safe_file(root, row["path"])
        if path.stat().st_size != row["size"] or sha(path) != row["sha256"]:
            raise ValueError("Repository manifest mismatch: " + row["path"])
    project_prefix = "current/EGA_v24/"
    project = [x for x in names if x.startswith(project_prefix)]
    if not project:
        raise ValueError("No current project files")
    bundles = [pack(root, project, output / "EGA-v24-project.zip", project_prefix, timestamp=timestamp)]
    if args.full:
        metadata = list(manifest.get("allowed_publication_metadata", []))
        if set(metadata) != PUBLICATION_METADATA or len(metadata) != len(PUBLICATION_METADATA):
            raise ValueError("Unexpected publication metadata paths")
        for name in metadata:
            safe_file(root, name)
        full_names = names + ["REPOSITORY_MANIFEST.json"] + metadata
        if len(set(full_names)) != len(full_names):
            raise ValueError("Duplicate full package input")
        bundles.append(pack(root, full_names, output / f"EGA-all-projects-with-Dot-v24-{stamp}.zip", timestamp=timestamp))
    assets = {"main.pdf": "EGA-v24-book.pdf", "single.tex": "EGA-v24-book.tex",
              "report.pdf": "EGA-v24-audit.pdf", "report_single.tex": "EGA-v24-audit.tex"}
    exported = []
    for source, target in assets.items():
        name = project_prefix + source
        if name not in names:
            raise ValueError("Required export is not present in the manifest: " + name)
        src = safe_file(root, name)
        dst = output / target
        shutil.copy2(src, dst)
        exported.append({"file": target, "size": dst.stat().st_size, "sha256": sha(dst)})
    result = {"edition": 24, "date": publication_date.isoformat(), "repository_manifest_sha256": sha(root / "REPOSITORY_MANIFEST.json"),
              "repository_files_checked": len(records), "bundles": bundles, "exports": exported,
              "scope": "Byte-verified packages of frozen engineering files; remote publication status is recorded separately; no claim of full mathematical proof verification"}
    (output / "PACKAGE_VERIFICATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sums = "".join(f"{sha(p)}  {p.name}\n" for p in sorted(output.iterdir()) if p.is_file())
    (output / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
