#!/usr/bin/env python3
"""Check continuation coverage and preservation of the ninth-edition body."""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
def main():
    old = json.loads((ROOT / "checks/baseline_structure_v9.json").read_text(encoding="utf-8"))
    book = (ROOT / "single.tex").read_text(encoding="utf-8")
    entry_re = r"\\ega(?:p|s|par|statement)\{([^}]+)\}"
    entries = re.findall(entry_re, book)
    tags = re.findall(r"\\tag\{([^}]+)\}", book)
    files = [ROOT / "continuations" / ("iv0_20_" + x + ".tex")
             for x in ["6a", "6b", "7a", "7b"]]
    new = "\n".join(p.read_text(encoding="utf-8") for p in files)
    new_entries = re.findall(entry_re, new)
    expected = [f"20.6.{i}" for i in range(1, 27)] + [f"20.7.{i}" for i in range(1, 21)]
    assert new_entries == expected, "New entries missing or out of order"
    missing_entries = list((collections.Counter(old["entries"]) - collections.Counter(entries)).elements())
    missing_tags = list((collections.Counter(old["tags"]) - collections.Counter(tags)).elements())
    hashes = json.loads((ROOT / "checks/baseline_body_v9_sha256.json").read_text(encoding="utf-8"))
    changed = [name for name, value in hashes.items()
               if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != value]
    assert not missing_entries and not missing_tags and not changed
    assert len(entries) == 2291 and len(tags) == 962
    result = {"entries": len(entries), "formula_tags": len(tags),
              "new_entries": len(new_entries),
              "new_tags": len(re.findall(r"\\tag\{([^}]+)\}", new)),
              "unchanged_old_body_files": len(hashes),
              "missing_old_entries": missing_entries, "missing_old_tags": missing_tags,
              "changed_old_body_files": changed}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
