#!/usr/bin/env python3
"""Generate edition-21 workflow pins only from a verified, present overlay.

Uses the reviewed edition-20 publication flow without granting new permissions.
It neither commits a workflow nor uploads or dispatches any remote operation.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

TEMPLATE_SHA256 = "7d0d2fb918b0e69d7cdca9c065a7720f4b3dfdf5e5a721e00209ab1fd51f3f0d"
BASE_COMMIT = "99cd048abd72adad984613aaa4f5fef86cd5a6c8"


def sha(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError("Expected an existing regular file: " + str(path))
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def replace_one(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise ValueError("Reviewed workflow edit no longer has one target: " + before)
    return source.replace(before, after)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--verification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    verification = args.verification.resolve()
    data = json.loads(verification.read_text(encoding="utf-8"))
    if (data.get("pass") is not True or data.get("edition") != 21
            or data.get("baseline_commit") != BASE_COMMIT
            or data.get("baseline_deferred_to_runner") != 0):
        raise ValueError("A real fully verified edition-21 freeze record is required")
    day = date.fromisoformat(data["snapshot_date"])
    if day.isoformat() != data["snapshot_date"]:
        raise ValueError("Noncanonical snapshot date")
    stamp = day.strftime("%Y%m%d")
    basename = f"EGA-v21-overlay-{stamp}.zip"
    if data["overlay_file"] != basename or data["release_tag"] != "v21-" + stamp:
        raise ValueError("Overlay and release names do not match the measured date")
    directory = verification.parent
    archive = directory / basename
    for field in ("overlay_zip_bytes", "overlay_file_count", "overlay_uncompressed_bytes"):
        if type(data.get(field)) is not int or data[field] <= 0:
            raise ValueError("Measured field must be a positive integer: " + field)
    if (not re.fullmatch(r"[0-9a-f]{64}", data["overlay_sha256"])
            or sha(archive) != data["overlay_sha256"]
            or archive.stat().st_size != data["overlay_zip_bytes"]):
        raise ValueError("Present overlay differs from the frozen archive")
    with zipfile.ZipFile(archive) as zipped:
        members = zipped.infolist()
        if (len(members) != data["overlay_file_count"]
                or sum(info.file_size for info in members) != data["overlay_uncompressed_bytes"]
                or len({info.filename for info in members}) != len(members)):
            raise ValueError("Present overlay member count or byte sum differs from freeze record")
    parts = data["parts"]
    if not isinstance(parts, list) or not 1 <= len(parts) <= 999:
        raise ValueError("Expected one to 999 actual measured parts")
    assembled = hashlib.sha256()
    sizes = []
    for number, row in enumerate(parts, 1):
        name = basename + f".part{number:03d}"
        if row["file"] != name or type(row["bytes"]) is not int:
            raise ValueError("Parts must have exact sequential names and measured byte counts")
        size = row["bytes"]
        if not 1 <= size <= 32 * 1024 * 1024:
            raise ValueError("Part size is outside the workflow range")
        if number < len(parts) and size != 32 * 1024 * 1024:
            raise ValueError("All parts except the last must be exactly 32 MiB")
        path = directory / name
        if sha(path) != row["sha256"] or path.stat().st_size != size:
            raise ValueError("Present part differs from its frozen bytes: " + name)
        with path.open("rb") as source:
            while block := source.read(1024 * 1024):
                assembled.update(block)
        sizes.append(size)
    if sum(sizes) != archive.stat().st_size or assembled.hexdigest() != sha(archive):
        raise ValueError("Actual ordered parts do not reconstruct the pinned overlay")

    template = root / ".github/workflows/publish-edition20.yml"
    if sha(template) != TEMPLATE_SHA256:
        raise ValueError("The source publishing workflow differs from the independently read template")
    workflow = template.read_text(encoding="utf-8")
    for before, after in (
        ("Edition20", "Edition21"), ("edition20", "edition21"),
        ("edition 20", "edition 21"), ("edition-20", "edition-21"),
        ("v20", "v21"), ("EDITION_20", "EDITION_21"),
        ("20261125", stamp),
        ("section12 source recollation with Dot and verified counterexamples",
         "section13 source recollation with Dot and scoped mathematical reviews"),
    ):
        workflow = workflow.replace(before, after)
    values = {
        "OVERLAY_ASSET": basename,
        "OVERLAY_SHA256": data["overlay_sha256"],
        "OVERLAY_ZIP_BYTES": str(data["overlay_zip_bytes"]),
        "OVERLAY_FILE_COUNT": str(data["overlay_file_count"]),
        "OVERLAY_UNCOMPRESSED_BYTES": str(data["overlay_uncompressed_bytes"]),
        "OVERLAY_PART_COUNT": str(len(parts)),
        "OVERLAY_PART_SIZES_JSON": json.dumps(sizes),
    }
    for key, value in values.items():
        pattern = rf"(?m)^      {re.escape(key)}: .+$"
        workflow, count = re.subn(pattern, "      " + key + ": " + json.dumps(value), workflow)
        if count != 1:
            raise ValueError("Expected one pinned workflow environment field: " + key)
    workflow = replace_one(
        workflow, f"      RELEASE_TAG: v21-{stamp}\n",
        f"      RELEASE_TAG: v21-{stamp}\n      SNAPSHOT_DATE: \"{day.isoformat()}\"\n",
    )
    workflow = replace_one(
        workflow, '            --total-bytes "$OVERLAY_UNCOMPRESSED_BYTES"\n',
        '            --total-bytes "$OVERLAY_UNCOMPRESSED_BYTES" \\\n'
        '            --snapshot-date "$SNAPSHOT_DATE"\n',
    )
    if any(token in workflow for token in ("edition20", "edition 20", "edition-20", "v20", "EDITION_20")):
        raise ValueError("An old-edition runtime target remains in the generated workflow")
    output = args.output.resolve()
    if output.exists() and output.read_text(encoding="utf-8") != workflow:
        raise ValueError("Refusing to overwrite a different workflow; review the new target separately")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(workflow, encoding="utf-8")
    print(json.dumps({
        "generated_workflow": str(output), "sha256": sha(output),
        "release_tag": data["release_tag"], "overlay_sha256": data["overlay_sha256"],
        "actual_parts_reverified": len(parts), "actual_zip_bytes": archive.stat().st_size,
        "remote_actions_performed": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
