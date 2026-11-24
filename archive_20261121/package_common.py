#!/usr/bin/env python3
"""Standard-library helpers for EGA handover package integrity.

These functions verify file bytes and paths, never mathematical correctness.
The package must remain unchanged while a check or restoration is running.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import tempfile

MANIFEST = "MANIFEST.json"
SUMS = "SHA256SUMS.txt"
RESTORE_INDEX = "04_history/RESTORE_INDEX.json"
METADATA_FILES = {MANIFEST, SUMS}
CHUNK_SIZE = 1024 * 1024
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


class PackageError(Exception):
    """An unsafe path, invalid record, changed file, or integrity mismatch."""


def relative_parts(value, label="path"):
    """Accept canonical, portable relative POSIX paths; never normalize input."""
    if not isinstance(value, str) or not value:
        raise PackageError(f"{label}: expected a non-empty relative path")
    if any(ord(c) < 32 or ord(c) == 127 or c in "\x85\u2028\u2029" for c in value):
        raise PackageError(f"{label}: control characters are forbidden")
    if "\\" in value or ":" in value or value.startswith("/"):
        raise PackageError(f"{label}: absolute, drive, ADS, or backslash path: {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise PackageError(f"{label}: empty, dot, or parent component: {value!r}")
    for part in parts:
        if part != part.rstrip(" .") or any(c in '<>"|?*' for c in part):
            raise PackageError(f"{label}: non-portable path component: {part!r}")
        device = part.split(".", 1)[0].upper()
        if (device in {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
                or re.fullmatch(r"(?:COM|LPT)[1-9¹²³]", device)):
            raise PackageError(f"{label}: reserved device name: {part!r}")
    if PureWindowsPath(value).drive:
        raise PackageError(f"{label}: drive or UNC path: {value!r}")
    return parts


def one_component(value, label):
    if len(relative_parts(value, label)) != 1:
        raise PackageError(f"{label}: expected one path component")
    return value


def validate_hash(value, label):
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise PackageError(f"{label}: expected lowercase SHA-256 hex")
    return value


def validate_size(value, label):
    if type(value) is not int or value < 0:
        raise PackageError(f"{label}: expected a non-negative integer")
    return value


def _lstat(path):
    try:
        info = path.lstat()
    except OSError as exc:
        raise PackageError(f"Cannot inspect {path}: {exc}") from exc
    attributes = getattr(info, "st_file_attributes", 0)
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if stat.S_ISLNK(info.st_mode) or attributes & reparse:
        raise PackageError(f"Links/reparse points are forbidden: {path}")
    return info


def absolute_path(value):
    return Path(os.path.abspath(os.path.expanduser(os.fspath(value))))


def require_directory(path):
    """Also reject links in existing ancestors of an absolute directory."""
    path = absolute_path(path)
    for ancestor in list(reversed(path.parents)) + [path]:
        if not stat.S_ISDIR(_lstat(ancestor).st_mode):
            raise PackageError(f"Expected a directory: {ancestor}")
    return path


def package_root(value):
    return require_directory(value)


def checked_file_path(root, relative):
    parts = relative_parts(relative)
    current = root
    if not stat.S_ISDIR(_lstat(current).st_mode):
        raise PackageError(f"Not a directory: {current}")
    for number, part in enumerate(parts):
        current = current / part
        info = _lstat(current)
        last = number == len(parts) - 1
        if last and not stat.S_ISREG(info.st_mode):
            raise PackageError(f"Expected a regular file: {current}")
        if not last and not stat.S_ISDIR(info.st_mode):
            raise PackageError(f"Expected a directory: {current}")
    return current


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


@contextlib.contextmanager
def open_regular(root, relative):
    path = checked_file_path(root, relative)
    before = _lstat(path)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise PackageError(f"Cannot open {path}: {exc}") from exc
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode) or _identity(opened) != _identity(before):
            raise PackageError(f"File changed while opening: {path}")
        yield handle
        if _identity(os.fstat(handle.fileno())) != _identity(opened):
            raise PackageError(f"File changed while reading: {path}")
        checked_file_path(root, relative)
        if _identity(_lstat(path)) != _identity(opened):
            raise PackageError(f"File path changed while reading: {path}")


def read_regular(root, relative):
    with open_regular(root, relative) as handle:
        return handle.read()


def digest_regular(root, relative):
    digest = hashlib.sha256()
    size = 0
    with open_regular(root, relative) as handle:
        for data in iter(lambda: handle.read(CHUNK_SIZE), b""):
            size += len(data)
            digest.update(data)
    return size, digest.hexdigest()


def inventory(root):
    """List all ordinary files; reject links and special files, even if unlisted."""
    result = []
    stack = [root]
    while stack:
        directory = stack.pop()
        if not stat.S_ISDIR(_lstat(directory).st_mode):
            raise PackageError(f"Expected a directory: {directory}")
        try:
            children = sorted(directory.iterdir(), key=lambda p: p.name)
        except OSError as exc:
            raise PackageError(f"Cannot list {directory}: {exc}") from exc
        for child in children:
            relative = child.relative_to(root).as_posix()
            relative_parts(relative)
            info = _lstat(child)
            if stat.S_ISDIR(info.st_mode):
                stack.append(child)
            elif stat.S_ISREG(info.st_mode):
                result.append(relative)
            else:
                raise PackageError(f"Special files are forbidden: {child}")
    return sorted(result)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _bad_constant(value):
    raise PackageError(f"Non-finite JSON constant: {value}")


def decode_json(data, label):
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=_bad_constant)
    except (UnicodeError, ValueError) as exc:
        raise PackageError(f"Invalid UTF-8 JSON in {label}: {exc}") from exc


def schema_one(value, label):
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int:
        raise PackageError(f"{label}: missing integer schema_version")
    if value["schema_version"] != 1:
        raise PackageError(f"{label}: unsupported schema_version")


def no_file_parent_collisions(paths, label):
    names = set(paths)
    for name in names:
        pieces = name.split("/")
        for index in range(1, len(pieces)):
            parent = "/".join(pieces[:index])
            if parent in names:
                raise PackageError(f"{label}: file is also a parent directory: {parent}")


def manifest_records(value):
    schema_one(value, MANIFEST)
    if not isinstance(value.get("files"), list):
        raise PackageError("MANIFEST.json: files must be a list")
    records = {}
    for entry in value["files"]:
        if not isinstance(entry, dict):
            raise PackageError("MANIFEST.json: a file entry is not an object")
        name = entry.get("path")
        relative_parts(name, "manifest path")
        if name in METADATA_FILES:
            raise PackageError(f"MANIFEST must not contain itself or SHA256SUMS: {name}")
        if name in records:
            raise PackageError(f"Duplicate manifest path: {name}")
        records[name] = {"path": name,
                         "bytes": validate_size(entry.get("bytes"), name),
                         "sha256": validate_hash(entry.get("sha256"), name)}
    no_file_parent_collisions(records, MANIFEST)
    return records


def checksum_records(data):
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise PackageError("SHA256SUMS.txt must be UTF-8") from exc
    result = {}
    for number, line in enumerate(text.splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise PackageError(f"Malformed SHA256SUMS line {number}")
        digest, name = match.groups()
        relative_parts(name, "checksum path")
        if name == SUMS:
            raise PackageError("SHA256SUMS must not list itself")
        if name in result:
            raise PackageError(f"Duplicate checksum path: {name}")
        result[name] = digest
    return result


def verify_tree(root, strict=False):
    root = package_root(root)
    sums = checksum_records(read_regular(root, SUMS))
    manifest_data = read_regular(root, MANIFEST)
    manifest_hash = hashlib.sha256(manifest_data).hexdigest()
    if sums.get(MANIFEST) != manifest_hash:
        raise PackageError("MANIFEST.json SHA-256 does not match SHA256SUMS.txt")
    records = manifest_records(decode_json(manifest_data, MANIFEST))
    expected_sums = set(records) | {MANIFEST}
    if set(sums) != expected_sums:
        missing = sorted(expected_sums - set(sums))
        extra = sorted(set(sums) - expected_sums)
        raise PackageError(f"Checksum/manifest path sets differ; missing={missing[:8]}, extra={extra[:8]}")
    actual_paths = set(inventory(root))
    missing = sorted(set(records) - actual_paths)
    if missing:
        raise PackageError(f"Missing payload files: {missing[:8]}")
    extra = sorted(actual_paths - set(records) - METADATA_FILES)
    if strict and extra:
        raise PackageError(f"Unlisted files in strict mode: {extra[:8]} (total {len(extra)})")
    total = 0
    for name, record in records.items():
        if sums[name] != record["sha256"]:
            raise PackageError(f"Manifest and checksum disagree: {name}")
        size, digest = digest_regular(root, name)
        if size != record["bytes"] or digest != record["sha256"]:
            raise PackageError(f"Size/SHA-256 mismatch: {name}")
        total += size
    return ({"pass": True, "root": str(root), "strict": bool(strict),
             "payload_files": len(records), "payload_bytes": total,
             "manifest_sha256": manifest_hash, "extra_files": extra,
             "scope": "file paths, sizes and SHA-256 only; not mathematical validation"}, records)


def _write_temporary(root, data):
    with tempfile.NamedTemporaryFile(mode="wb", prefix=".ega-integrity-", dir=root,
                                     delete=False) as handle:
        path = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o644)
    return path


def refresh_tree(root):
    root = package_root(root)
    paths = inventory(root)
    records = []
    for name in paths:
        if name in METADATA_FILES:
            continue
        size, digest = digest_regular(root, name)
        records.append({"path": name, "bytes": size, "sha256": digest})
    manifest_data = (json.dumps({"schema_version": 1, "files": records},
                                ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    manifest_hash = hashlib.sha256(manifest_data).hexdigest()
    checksum_map = {entry["path"]: entry["sha256"] for entry in records}
    checksum_map[MANIFEST] = manifest_hash
    sums_data = "".join(f"{checksum_map[name]}  {name}\n" for name in sorted(checksum_map)).encode("utf-8")
    temporary = []
    try:
        for data in (manifest_data, sums_data):
            temporary.append(_write_temporary(root, data))
        for source, name in zip(temporary, (MANIFEST, SUMS)):
            destination = root / name
            if os.path.lexists(destination):
                checked_file_path(root, name)
            os.replace(source, destination)
    finally:
        for path in temporary:
            if path.exists():
                path.unlink()
    return {"root": str(root), "payload_files": len(records),
            "payload_bytes": sum(record["bytes"] for record in records),
            "manifest_sha256": manifest_hash,
            "scope": "refreshed byte inventory only; no mathematical or translation validation"}
