#!/usr/bin/env python3
"""Freeze the locally verified edition-20 overlay; old history is checked on the runner.

Run only after final build/visual records and handover documents have been saved.
This script does not upload, apply, or claim to verify unmaterialized old files.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import stat
import zipfile

BASE = '997597a5476cb07338a9b2feef61077ae795774e'
METADATA = ['.github/workflows/import-20261124.yml', '.github/workflows/publish-archive-supplement-20261125.yml', '.github/workflows/publish-edition18.yml', '.github/workflows/publish-edition19.yml', 'ARCHIVE_SUPPLEMENT_IMPORT.json', 'EDITION_18_IMPORT.json', 'EDITION_19_IMPORT.json', 'IMPORT_RECEIPT.json', '.github/workflows/publish-edition20.yml', 'EDITION_20_IMPORT.json']
ROOT_DOCS = ['README.md', 'AGENTS.md', 'CONTINUE_HERE.md']
TOOLS = ['tools/apply_edition20_update.py', 'tools/package_edition20.py']
TEMP_SUFFIXES = {'.aux', '.xdv', '.out', '.toc', '.fls', '.fdb_latexmk', '.pyc'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Delivery output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    project = root / 'current/EGA_v20'
    for name in ['current_structure_verification.json', 'current_build_log_summary.json',
                 'current_pdf_parity.json', 'visual_verification_summary.json']:
        if json.loads((project / 'checks' / name).read_text())['pass'] is not True:
            raise ValueError('Required actual verification has not passed: ' + name)
    state = json.loads((project / 'HANDOVER_STATE.json').read_text())
    if state['status'] != 'build_and_review_verified' or state['all_books_finished'] is not False:
        raise ValueError('Handover status has not been finalized accurately')
    baseline_path = root / 'snapshots/20261125-v20/REPOSITORY_MANIFEST.json'
    old = json.loads(baseline_path.read_text())
    mapping = {row['path']: row for row in old['files']}
    materialized, deferred = 0, 0
    for row in old['files']:
        if row['path'] in ROOT_DOCS:
            candidate = root / 'snapshots/20261125-v20' / row['path']
        else:
            candidate = root / row['path']
        if candidate.is_file():
            if candidate.stat().st_size != row['size'] or sha(candidate) != row['sha256']:
                raise ValueError('Materialized baseline mismatch: ' + row['path'])
            materialized += 1
        else:
            deferred += 1
    selected = ROOT_DOCS + TOOLS
    for prefix in ['current/EGA_v20', 'snapshots/20261125-v20']:
        for path in sorted((root / prefix).rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlink in new payload: ' + str(path))
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if '__pycache__' in path.parts or rel.startswith('current/EGA_v20/runtime/'):
                continue
            if path.suffix in TEMP_SUFFIXES or path.name.endswith('.synctex.gz'):
                continue
            selected.append(rel)
    if len(selected) != len(set(selected)):
        raise ValueError('Duplicate selected path')
    for name in selected:
        path = root / name
        if name in mapping and name not in ROOT_DOCS:
            raise ValueError('Unapproved overwrite: ' + name)
        mapping[name] = {'path': name, 'size': path.stat().st_size, 'sha256': sha(path)}
    manifest = {
        'schema_version': 3, 'snapshot_date': '2026-11-25', 'time_zone': 'Asia/Shanghai',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_cutoff': old.get('source_cutoff'),
        'scope': 'Preserve every previous engineering payload and all Dot archives; add edition20 '
                 'French/English recollation of first essay section12, actual build/review '
                 'records and continuation state. No claim of all volumes or all proofs finished.',
        'baseline_commit': BASE, 'baseline_manifest_sha256': sha(baseline_path),
        'allowed_publication_metadata': METADATA,
        'files': [mapping[name] for name in sorted(mapping)],
    }
    manifest_path = root / 'REPOSITORY_MANIFEST.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    selected.append('REPOSITORY_MANIFEST.json')
    archive = out / 'EGA-v20-overlay-20261125.zip'
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(selected):
            path = root / name
            info = zipfile.ZipInfo(name, (2026, 11, 25, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            with path.open('rb') as source, z.open(info, 'w', force_zip64=True) as dest:
                shutil.copyfileobj(source, dest)
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) != len(selected) or set(z.namelist()) != set(selected) or z.testzip():
            raise ValueError('Overlay member/CRC mismatch')
        for info in z.infolist():
            path = root / info.filename
            with z.open(info) as source:
                if info.file_size != path.stat().st_size or hashlib.file_digest(source, 'sha256').hexdigest() != sha(path):
                    raise ValueError('Overlay member bytes mismatch: ' + info.filename)
    part_records = []
    with archive.open('rb') as source:
        i = 1
        while data := source.read(32 * 1024 * 1024):
            part = out / (archive.name + f'.part{i:03d}')
            part.write_bytes(data)
            part_records.append({'file': part.name, 'bytes': len(data), 'sha256': sha(part)})
            i += 1
    rebuilt = hashlib.sha256()
    for row in part_records:
        with (out / row['file']).open('rb') as source:
            while block := source.read(1024 * 1024):
                rebuilt.update(block)
    if rebuilt.hexdigest() != sha(archive):
        raise ValueError('Ordered part reassembly hash mismatch')
    result = {
        'pass': True, 'scope': 'All overlay member bytes and ordered parts verified; only materialized '
        'old baseline files checked locally. Actual full-history validation is a mandatory runner gate.',
        'baseline_materialized_checked': materialized, 'baseline_deferred_to_runner': deferred,
        'manifest_payload_records': len(mapping), 'overlay_file_count': len(selected),
        'overlay_uncompressed_bytes': sum((root / name).stat().st_size for name in selected),
        'overlay_zip_bytes': archive.stat().st_size, 'overlay_sha256': sha(archive),
        'parts': part_records,
    }
    (out / 'OVERLAY_VERIFICATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
