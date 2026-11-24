#!/usr/bin/env python3
"""Keep historical source bytes independent of the editable current project."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1] / "release_20261121/EGA_20261121_Dot_handover"
index_path = ROOT / "04_history/RESTORE_INDEX.json"
index = json.loads(index_path.read_text(encoding="utf-8"))
prefix = "01_project/EGA_v17/"
changes = []
objects = {}
for version, description in index["versions"].items():
    for row in description["files"]:
        old_path = row["stored_path"]
        if not old_path.startswith(prefix):
            continue
        within_project = old_path[len(prefix):]
        if within_project.startswith(("vendor/", "history/", "checks/")):
            continue
        source = ROOT / old_path
        data = source.read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
        digest = row["sha256"]
        relative = f"04_history/content/{digest[:2]}/{digest}"
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == data
        else:
            shutil.copy2(source, target)
        row["stored_path"] = relative
        changes.append({"version": version, "original_path": row["original_path"],
                        "previous_stored_path": old_path, "immutable_stored_path": relative,
                        "sha256": digest, "bytes": len(data)})
        objects[digest] = len(data)
index["editable_sources_frozen"] = True
index["immutable_history_note"] = (
    "Historical editable TeX/source/build files are stored as immutable content objects. "
    "Shared original source PDFs, raw Dot archives, vendor files and explicitly historical "
    "directories must remain unchanged; work on copies if they ever need editing."
)
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
result = {"pass": True, "changed_history_references": len(changes),
          "unique_editable_source_objects": len(objects), "unique_bytes": sum(objects.values()),
          "original_paths_and_sha256_unchanged": True, "changes": changes}
(ROOT / "07_integration_records/20261121/immutable_source_snapshots.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "changes"}, ensure_ascii=False, indent=2))
