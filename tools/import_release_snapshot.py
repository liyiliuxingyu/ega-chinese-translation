#!/usr/bin/env python3
"""Import one hash-pinned engineering snapshot, without executing archived projects."""
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

MANIFEST = 'REPOSITORY_MANIFEST.json'
RECEIPT = 'IMPORT_RECEIPT.json'
BOOTSTRAP = {'README.md', 'tools/import_release_snapshot.py',
             '.github/workflows/import-20261124.yml'}


def digest(stream) -> str:
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--file-count', required=True, type=int)
    parser.add_argument('--total-bytes', required=True, type=int)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{64}', args.sha256):
        raise ValueError('Expected SHA-256 must contain exactly 64 lowercase hexadecimal digits')
    root = args.root.resolve()
    receipt_path = root / RECEIPT
    if not args.verify_only and receipt_path.exists():
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
        if receipt.get('archive_sha256') != args.sha256:
            raise ValueError('A different snapshot has already been imported')
        print('This snapshot was already imported; no working files were overwritten.')
        return 0
    with args.archive.open('rb') as stream:
        if digest(stream) != args.sha256:
            raise ValueError('Archive SHA-256 mismatch')
    with zipfile.ZipFile(args.archive) as archive:
        members = archive.infolist()
        names = set()
        total_bytes = 0
        for item in members:
            name = item.filename
            path = PurePosixPath(name)
            mode = stat.S_IFMT(item.external_attr >> 16)
            if (not name or '\\' in name or path.as_posix() != name or path.is_absolute() or '..' in path.parts
                    or any(part.lower() == '.git' for part in path.parts)
                    or name in names or item.is_dir() or mode not in (0, stat.S_IFREG)
                    or name.startswith('.github/') or name == RECEIPT):
                raise ValueError(f'Unsafe, unexpected, or duplicate ZIP member: {name}')
            names.add(name)
            total_bytes += item.file_size
        if len(members) != args.file_count or total_bytes != args.total_bytes:
            raise ValueError('Archive member count or total size mismatch')
        manifest = json.loads(archive.read(MANIFEST).decode('utf-8'))
        records = manifest['files']
        expected_names = [item['path'] for item in records]
        if len(set(expected_names)) != len(expected_names):
            raise ValueError('Duplicate manifest entries')
        if set(expected_names) | {MANIFEST} != names:
            raise ValueError('Archive and manifest paths do not agree')
        for item in records:
            info = archive.getinfo(item['path'])
            with archive.open(info) as stream:
                if info.file_size != item['size'] or digest(stream) != item['sha256']:
                    raise ValueError(f'Manifest mismatch: {item["path"]}')
        if args.verify_only:
            print(json.dumps({'ok': True, 'archive_sha256': args.sha256,
                              'files': len(members), 'bytes': total_bytes}))
            return 0
        tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode('utf-8').split('\0')
        unexpected = set(filter(None, tracked)) - BOOTSTRAP
        if unexpected:
            raise ValueError('Refusing to overwrite an already populated repository')
        for name in names:
            target = root / name
            if target.is_symlink():
                raise ValueError(f'Refusing to replace a symlink: {name}')
            if target.exists() and name not in BOOTSTRAP:
                raise ValueError(f'Refusing to replace an unexpected existing file: {name}')
            for parent in target.parents:
                if parent == root:
                    break
                if parent.is_symlink():
                    raise ValueError(f'Refusing to traverse a symlink: {name}')
        for item in members:
            target = root / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
            target.chmod(0o755 if (item.external_attr >> 16) & 0o111 else 0o644)
        receipt_path.write_text(json.dumps({
            'archive_sha256': args.sha256,
            'archive_files': len(members),
            'archive_uncompressed_bytes': total_bytes,
            'imported_at_utc': datetime.now(timezone.utc).isoformat(),
            'scope': 'byte-preserving repository import; no new translation or mathematical certification'
        }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Snapshot imported. Run tools/verify_repository.py --strict before committing.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
