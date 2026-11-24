#!/usr/bin/env python3
"""Restore ordinary files from an indexed historical version, never a ZIP container."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

sys.dont_write_bytecode = True
from package_common import (CHUNK_SIZE, RESTORE_INDEX, PackageError, _lstat,
                            absolute_path, decode_json, digest_regular,
                            no_file_parent_collisions, one_component,
                            open_regular, read_regular, relative_parts,
                            require_directory, schema_one, validate_hash,
                            validate_size, verify_tree)


def read_index(root, manifest):
    if RESTORE_INDEX not in manifest:
        raise PackageError("RESTORE_INDEX.json is not covered by the package manifest")
    index = decode_json(read_regular(root, RESTORE_INDEX), RESTORE_INDEX)
    schema_one(index, RESTORE_INDEX)
    versions = index.get("versions")
    if not isinstance(versions, dict) or not versions:
        raise PackageError("RESTORE_INDEX.json: versions must be a non-empty object")
    for name in versions:
        one_component(name, "version key")
    return versions


def version_records(versions, name, manifest):
    if name not in versions:
        raise PackageError(f"Unknown version {name!r}; available: {', '.join(sorted(versions))}")
    version = versions[name]
    if not isinstance(version, dict):
        raise PackageError("Version entry must be an object")
    root_name = one_component(version.get("root_name"), "historical root_name")
    archive = version.get("archive")
    if not isinstance(archive, dict):
        raise PackageError("Version archive metadata must be an object")
    one_component(archive.get("file_name"), "original archive file_name")
    validate_size(archive.get("bytes"), "original archive bytes")
    validate_hash(archive.get("sha256"), "original archive SHA-256")
    entries = version.get("files")
    if not isinstance(entries, list):
        raise PackageError("Version files must be a list")
    originals = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PackageError("A restore file entry is not an object")
        original = entry.get("original_path")
        stored = entry.get("stored_path")
        relative_parts(original, "original_path")
        relative_parts(stored, "stored_path")
        if original in originals:
            raise PackageError(f"Duplicate original_path: {original}")
        size = validate_size(entry.get("bytes"), original)
        digest = validate_hash(entry.get("sha256"), original)
        record = manifest.get(stored)
        if record is None:
            raise PackageError(f"Restore source is not in the package manifest: {stored}")
        if record["bytes"] != size or record["sha256"] != digest:
            raise PackageError(f"Restore index and package manifest disagree: {stored}")
        originals[original] = {"original_path": original, "stored_path": stored,
                               "bytes": size, "sha256": digest}
    no_file_parent_collisions(originals, "restore index")
    return root_name, archive, [originals[key] for key in sorted(originals)]


def empty_destination(value, package):
    destination = absolute_path(value)
    if destination == package or package in destination.parents:
        raise PackageError("The restore destination must be outside the package")
    if os.path.lexists(destination):
        require_directory(destination)
        if any(destination.iterdir()):
            raise PackageError(f"Restore destination is not empty: {destination}")
    else:
        require_directory(destination.parent)
        destination.mkdir()
    return destination


def make_parent_directories(root, relative):
    parts = relative_parts(relative)
    current = root
    for part in parts[:-1]:
        current = current / part
        if not os.path.lexists(current):
            current.mkdir()
        if not stat.S_ISDIR(_lstat(current).st_mode):
            raise PackageError(f"Restore parent is not a directory: {current}")
    return current / parts[-1]


def restore(root, version_name, destination, strict=False):
    verification, manifest = verify_tree(root, strict=strict)
    root = Path(verification["root"])
    versions = read_index(root, manifest)
    root_name, archive, entries = version_records(versions, version_name, manifest)
    # verify_tree checked every stored source before any destination is created.
    destination = empty_destination(destination, root)
    restored = destination / root_name
    restored.mkdir()  # Exclusive: the destination was empty; never exist_ok.
    try:
        for entry in entries:
            target = make_parent_directories(restored, entry["original_path"])
            flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
                     | getattr(os, "O_NOFOLLOW", 0))
            descriptor = os.open(target, flags, 0o644)
            with os.fdopen(descriptor, "wb") as output:
                with open_regular(root, entry["stored_path"]) as source:
                    for data in iter(lambda: source.read(CHUNK_SIZE), b""):
                        output.write(data)
                output.flush()
                os.fsync(output.fileno())
        # A second pass reads every restored file; it is not a copy-time counter.
        for entry in entries:
            size, digest = digest_regular(restored, entry["original_path"])
            if size != entry["bytes"] or digest != entry["sha256"]:
                raise PackageError(f"Restored file verification failed: {entry['original_path']}")
    except (PackageError, OSError) as exc:
        raise PackageError(f"Restore failed; partial output remains at {restored}. {exc}") from exc
    return {"pass": True, "version": version_name, "restored_root": str(restored),
            "files": len(entries), "bytes": sum(entry["bytes"] for entry in entries),
            "all_restored_files_rehashed": True, "original_archive_metadata": archive,
            "archive_container_recreated": False,
            "scope": "ordinary file paths and bytes only; no ZIP reconstruction or math validation"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="package root; defaults to this script's directory")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--version", help="version key read from RESTORE_INDEX.json; use --list to inspect")
    mode.add_argument("--list", action="store_true", help="verify the package and list indexed version keys")
    parser.add_argument("--destination", type=Path,
                        help="empty or new directory, outside the package; its parent must exist")
    parser.add_argument("--strict", action="store_true", help="reject unlisted package files as well")
    parser.add_argument("--json", action="store_true", help="print a machine-readable result")
    args = parser.parse_args()
    if args.version is not None and args.destination is None:
        parser.error("--destination is required with --version")
    if args.list and args.destination is not None:
        parser.error("--destination cannot be used with --list")
    try:
        if args.list:
            report, manifest = verify_tree(args.root, strict=args.strict)
            versions = read_index(Path(report["root"]), manifest)
            result = {"pass": True, "versions": sorted(versions)}
        else:
            one_component(args.version, "version key")
            result = restore(args.root, args.version, args.destination, strict=args.strict)
    except (PackageError, OSError) as exc:
        if args.json:
            print(json.dumps({"pass": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"Restore failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.list:
        print("Available versions: " + ", ".join(result["versions"]))
    else:
        print(f"Restored and rehashed {result['files']} ordinary files to {result['restored_root']}.")
        print("Original paths and bytes were restored; the original ZIP container was NOT recreated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
