#!/usr/bin/env python3
"""Apply the hash-pinned EGA edition 18 overlay, preserving all raw archives."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import zipfile

BASE_COMMIT = "28f090c03092bfa38c23eeb6bfeffb0471e123a5"
WORKFLOW = ".github/workflows/publish-edition18.yml"
MANIFEST = "REPOSITORY_MANIFEST.json"
RECEIPT = "EDITION_18_IMPORT.json"
ROOT_UPDATES = {"README.md", "AGENTS.md", "CONTINUE_HERE.md", MANIFEST}
NEW_PREFIXES = ("current/EGA_v18/", "snapshots/20261124/")
NEW_TOOLS = {"tools/apply_edition18_update.py", "tools/package_edition18.py"}


def digest(stream):
    return hashlib.file_digest(stream, "sha256").hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    return (bool(name) and "\\" not in name and p.as_posix() == name
            and not p.is_absolute() and ".." not in p.parts
            and all(x.lower() != ".git" for x in p.parts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--file-count", required=True, type=int)
    parser.add_argument("--total-bytes", required=True, type=int)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch("[0-9a-f]{64}", args.sha256):
        raise ValueError("Invalid SHA-256")
    root = args.root.resolve()
    receipt = root / RECEIPT
    already_applied = False
    if receipt.exists() and not args.verify_only:
        old = json.loads(receipt.read_text(encoding="utf-8"))
        if old.get("overlay_sha256") != args.sha256:
            raise ValueError("Another edition 18 overlay has already been applied")
        already_applied = True
    with args.archive.open("rb") as stream:
        if digest(stream) != args.sha256:
            raise ValueError("Overlay SHA-256 mismatch")
    if not args.verify_only and not already_applied:
        subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                        BASE_COMMIT, "HEAD"], check=True)
        changed = subprocess.check_output(["git", "-C", str(root), "diff", "--name-only",
                                           BASE_COMMIT, "HEAD"]).decode().splitlines()
        if set(changed) != {WORKFLOW}:
            raise ValueError("Remote base changed beyond the reviewed publishing workflow")
        if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]):
            raise ValueError("Refusing to apply overlay to a dirty checkout")

    with zipfile.ZipFile(args.archive) as archive:
        members = archive.infolist()
        names = set()
        total = 0
        for info in members:
            name = info.filename
            mode = stat.S_IFMT(info.external_attr >> 16)
            if (not safe_name(name) or name in names or info.is_dir()
                    or mode not in (0, stat.S_IFREG)
                    or not (name in ROOT_UPDATES | NEW_TOOLS or name.startswith(NEW_PREFIXES))):
                raise ValueError("Unexpected or unsafe overlay path: " + name)
            names.add(name)
            total += info.file_size
        if len(names) != args.file_count or total != args.total_bytes:
            raise ValueError("Overlay file count or uncompressed size mismatch")
        if MANIFEST not in names:
            raise ValueError("Missing repository manifest")
        manifest = json.loads(archive.read(MANIFEST).decode("utf-8"))
        rows = manifest["files"]
        mapping = {}
        for row in rows:
            name = row["path"]
            if not safe_name(name) or name in mapping:
                raise ValueError("Unsafe or duplicate manifest entry")
            mapping[name] = row
        if not names - {MANIFEST} <= mapping.keys():
            raise ValueError("Overlay contains files absent from the new manifest")
        # Every payload byte is validated before any write. For unchanged files,
        # the new manifest is checked against the actual checkout on disk.
        for name, row in mapping.items():
            if name in names:
                info = archive.getinfo(name)
                with archive.open(info) as stream:
                    valid = info.file_size == row["size"] and digest(stream) == row["sha256"]
            else:
                path = root / name
                if any(x.is_symlink() for x in path.parents if x != root):
                    raise ValueError("Refusing symlink traversal: " + name)
                valid = path.is_file() and not path.is_symlink() and path.stat().st_size == row["size"]
                if valid:
                    with path.open("rb") as stream:
                        valid = digest(stream) == row["sha256"]
            if not valid:
                raise ValueError("New manifest mismatch: " + name)
        if already_applied:
            if (root / MANIFEST).read_bytes() != archive.read(MANIFEST):
                raise ValueError("Applied repository manifest no longer matches the overlay")
            for name, row in mapping.items():
                path = root / name
                if (not path.is_file() or path.is_symlink()
                        or any(x.is_symlink() for x in path.parents if x != root)):
                    raise ValueError("Applied file missing or unsafe: " + name)
                with path.open("rb") as stream:
                    if path.stat().st_size != row["size"] or digest(stream) != row["sha256"]:
                        raise ValueError("Applied file has changed: " + name)
            subprocess.run([sys.executable, str(root / "tools/verify_repository.py"),
                            "--root", str(root), "--strict"], check=True)
            print("The same overlay and every current payload file were verified; no files overwritten.")
            return 0
        if not args.verify_only:
            baseline = json.loads((root / MANIFEST).read_text(encoding="utf-8"))["files"]
            for row in baseline:
                name = row["path"]
                if name not in mapping:
                    raise ValueError("Previous payload file omitted: " + name)
                if name not in ROOT_UPDATES and mapping[name] != row:
                    raise ValueError("Previous payload bytes would change: " + name)
                if name in ROOT_UPDATES:
                    path = root / name
                    with path.open("rb") as stream:
                        if path.stat().st_size != row["size"] or digest(stream) != row["sha256"]:
                            raise ValueError("Existing root document changed: " + name)
            for name in names:
                target = root / name
                if target.exists() and name not in ROOT_UPDATES:
                    raise ValueError("Refusing to overwrite non-root existing file: " + name)
                if target.is_symlink() or any(x.is_symlink() for x in target.parents if x != root):
                    raise ValueError("Refusing symlink traversal")
        if args.verify_only:
            print(json.dumps({"ok": True, "overlay_files": len(names),
                              "overlay_bytes": total, "repository_records_checked": len(rows),
                              "scope": "Overlay and reconstructed repository bytes only"}))
            return 0
        for info in members:
            target = root / info.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            target.chmod(0o755 if (info.external_attr >> 16) & 0o111 else 0o644)
    receipt.write_text(json.dumps({
        "edition": 18, "base_commit": BASE_COMMIT,
        "overlay_sha256": args.sha256, "overlay_files": args.file_count,
        "overlay_uncompressed_bytes": args.total_bytes,
        "applied_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Publication of locally built, source-mapped edition 18; no claim of a complete mathematical audit"
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Edition 18 applied; immutable archives preserved. Verify the full repository before committing.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, zipfile.BadZipFile, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
