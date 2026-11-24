#!/usr/bin/env python3
"""Verify the byte-level 2026-11-24 publication manifest; no mathematical claims."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / 'REPOSITORY_MANIFEST.json').read_text(encoding='utf-8'))
    records = manifest['files']
    seen, problems = set(), []
    total = 0
    for item in records:
        name = item['path']
        rel = Path(name)
        if rel.is_absolute() or '..' in rel.parts or '.git' in rel.parts or name in seen:
            problems.append({'path': name, 'error': 'unsafe or duplicate manifest path'})
            continue
        seen.add(name)
        path = root / rel
        if path.is_symlink() or not path.is_file():
            problems.append({'path': name, 'error': 'missing or non-regular file'})
        elif path.stat().st_size != item['size'] or sha256(path) != item['sha256']:
            problems.append({'path': name, 'error': 'size or SHA-256 mismatch'})
        else:
            total += item['size']
    allowed = set(manifest.get('allowed_publication_metadata', [])) | {'REPOSITORY_MANIFEST.json'}
    if args.strict:
        for path in root.rglob('*'):
            rel = path.relative_to(root)
            if '.git' in rel.parts or '__pycache__' in rel.parts:
                continue
            if path.is_file() and rel.as_posix() not in seen | allowed:
                problems.append({'path': rel.as_posix(), 'error': 'unlisted extra file'})
    print(json.dumps({'ok': not problems, 'files_checked': len(seen), 'verified_bytes': total,
                      'mathematical_validation': False, 'problems': problems}, ensure_ascii=False, indent=2))
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
