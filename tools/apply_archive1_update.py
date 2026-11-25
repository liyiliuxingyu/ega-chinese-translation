#!/usr/bin/env python3
"""Apply an archive-only supplement; preserve all edition-19 manuscript bytes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, zipfile
from pathlib import Path, PurePosixPath

BASE_COMMIT = '4daf708a87069e2a6e28c22a29d3e3af26880f0b'
WORKFLOW = '.github/workflows/publish-archive-supplement-20261125.yml'
MANIFEST = 'REPOSITORY_MANIFEST.json'
RECEIPT = 'ARCHIVE_SUPPLEMENT_IMPORT.json'
ROOT_UPDATES = {'README.md', 'AGENTS.md', 'CONTINUE_HERE.md', MANIFEST}
SNAPSHOT = 'snapshots/20261125-archive1/'
NEW_PREFIXES = ('archive_supplement_20261125/', SNAPSHOT)
NEW_TOOLS = {'tools/apply_archive1_update.py', 'tools/package_archive1.py'}
OLD_METADATA = {'.github/workflows/import-20261124.yml', 'IMPORT_RECEIPT.json',
                '.github/workflows/publish-edition18.yml', 'EDITION_18_IMPORT.json',
                '.github/workflows/publish-edition19.yml', 'EDITION_19_IMPORT.json'}
PUBLICATION_METADATA = OLD_METADATA | {WORKFLOW, RECEIPT}

def digest(stream):
    return hashlib.file_digest(stream, 'sha256').hexdigest()

def safe_name(name):
    if not isinstance(name, str) or any(c in name for c in ('\\', '\0', '\r', '\n')):
        return False
    path = PurePosixPath(name)
    return bool(name) and path.as_posix() == name and not path.is_absolute() and '..' not in path.parts and all(x.lower() != '.git' for x in path.parts)

def allowed_overlay(name):
    return name in ROOT_UPDATES | NEW_TOOLS or name.startswith(NEW_PREFIXES)

def regular(root, name):
    if not safe_name(name): raise ValueError('Unsafe path: '+repr(name))
    path = root/name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('Missing, external, or nonregular file: '+name)
    if any(p.is_symlink() for p in path.parents if p != root):
        raise ValueError('Symlink traversal: '+name)
    return path

def tree(root, ref):
    raw = subprocess.check_output(['git','-C',str(root),'ls-tree','-r','-z',ref])
    result = {}
    for item in raw.split(b'\0'):
        if not item: continue
        meta, name = item.split(b'\t',1)
        mode, kind, sha = meta.decode('ascii').split()
        name = name.decode('utf-8')
        if not safe_name(name) or kind != 'blob' or mode not in ('100644','100755'):
            raise ValueError('Unsupported tracked file: '+name)
        result[name] = (mode, kind, sha)
    return result

def git_bytes(root, ref, name):
    return subprocess.check_output(['git','-C',str(root),'show',ref+':'+name])

def manifest_mapping(manifest, expected_metadata):
    metadata = manifest.get('allowed_publication_metadata')
    if not isinstance(metadata,list) or len(metadata) != len(expected_metadata) or set(metadata) != expected_metadata:
        raise ValueError('Unexpected publication metadata set')
    rows = manifest.get('files')
    if not isinstance(rows,list): raise ValueError('Manifest files must be a list')
    result = {}
    for row in rows:
        name = row.get('path')
        if (not safe_name(name) or name in result or name == MANIFEST or name in expected_metadata
            or type(row.get('size')) is not int or row['size'] < 0
            or not isinstance(row.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',row['sha256'])):
            raise ValueError('Invalid manifest record: '+repr(name))
        result[name] = row
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    parser.add_argument('--sha256',required=True)
    parser.add_argument('--file-count',required=True,type=int)
    parser.add_argument('--total-bytes',required=True,type=int)
    parser.add_argument('--root',type=Path,default=Path.cwd())
    parser.add_argument('--verify-only',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch('[0-9a-f]{64}',args.sha256) or args.file_count <= 0 or args.total_bytes <= 0:
        raise ValueError('Exact positive measured archive values are required')
    root=args.root.resolve()
    with args.archive.open('rb') as stream:
        if digest(stream) != args.sha256: raise ValueError('Overlay SHA-256 mismatch')
    if subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=all']):
        raise ValueError('Refusing a dirty checkout, including untracked files')
    subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE_COMMIT,'HEAD'],check=True)
    base=tree(root,BASE_COMMIT)
    head=tree(root,'HEAD')
    receipt_path=root/RECEIPT
    applied=receipt_path.is_file()
    if applied:
        prior=json.loads(regular(root,RECEIPT).read_text())
        if (prior.get('base_commit') != BASE_COMMIT or prior.get('overlay_sha256') != args.sha256
            or prior.get('overlay_files') != args.file_count or prior.get('overlay_uncompressed_bytes') != args.total_bytes):
            raise ValueError('A different archive supplement is already applied')
    # Protect all old tracked files and their modes, not merely old manifest rows.
    for name,identity in base.items():
        if name not in head: raise ValueError('Old tracked file was removed: '+name)
        if head[name] != identity and not (applied and name in ROOT_UPDATES):
            raise ValueError('Protected old file or mode changed: '+name)
    extra=set(head)-set(base)
    if not applied and extra - {WORKFLOW}:
        raise ValueError('Fresh checkout has changes beyond the new publishing workflow')
    if applied and any(not (allowed_overlay(n) or n in {WORKFLOW,RECEIPT}) for n in extra):
        raise ValueError('Applied checkout has unexpected added tracked files')
    old_manifest_bytes=git_bytes(root,BASE_COMMIT,MANIFEST)
    old_rows=manifest_mapping(json.loads(old_manifest_bytes),OLD_METADATA)

    with zipfile.ZipFile(args.archive) as archive:
        infos=archive.infolist(); names=set(); total=0
        for info in infos:
            name=info.filename
            if (not safe_name(name) or not allowed_overlay(name) or name in names or info.is_dir()
                or stat.S_IFMT(info.external_attr>>16) not in (0,stat.S_IFREG)):
                raise ValueError('Unexpected or unsafe overlay member: '+repr(name))
            names.add(name); total+=info.file_size
        if len(names) != args.file_count or total != args.total_bytes:
            raise ValueError('Overlay file count or uncompressed size mismatch')
        required=ROOT_UPDATES | NEW_TOOLS | {SNAPSHOT+n for n in ROOT_UPDATES} | {
            'archive_supplement_20261125/AUDIT_REPORT.md','archive_supplement_20261125/AUDIT_SUMMARY.json'}
        if not required <= names: raise ValueError('Missing required overlay files: '+repr(sorted(required-names)))
        mapping=manifest_mapping(json.loads(archive.read(MANIFEST)),PUBLICATION_METADATA)
        projected=(set(base)|names|{WORKFLOW,RECEIPT})-PUBLICATION_METADATA-{MANIFEST}
        if set(mapping) != projected:
            raise ValueError('New manifest paths differ from the exact preserved-plus-added tree')
        for name,row in old_rows.items():
            if name not in mapping: raise ValueError('Old payload omitted: '+name)
            if name not in ROOT_UPDATES and mapping[name] != row:
                raise ValueError('Old payload record would change: '+name)
        # Four frozen root originals, including the previous manifest, must be kept.
        for name in ROOT_UPDATES:
            if archive.read(SNAPSHOT+name) != git_bytes(root,BASE_COMMIT,name):
                raise ValueError('Snapshot is not the exact previous root file: '+name)
        for name,row in mapping.items():
            if name in names:
                info=archive.getinfo(name)
                with archive.open(info) as stream:
                    ok=info.file_size==row['size'] and digest(stream)==row['sha256']
            else:
                path=regular(root,name)
                with path.open('rb') as stream:
                    ok=path.stat().st_size==row['size'] and digest(stream)==row['sha256']
            if not ok: raise ValueError('New manifest byte mismatch: '+name)
        # No symlink traversal or pre-existing target may be silently overwritten.
        for name in names:
            path=root/name
            if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=root):
                raise ValueError('Unsafe extraction target: '+name)
            if not path.resolve().is_relative_to(root): raise ValueError('External extraction target')
            if path.exists() and name not in ROOT_UPDATES and not applied:
                raise ValueError('Refusing to overwrite existing non-root file: '+name)
        if applied:
            if regular(root,MANIFEST).read_bytes() != archive.read(MANIFEST):
                raise ValueError('Applied manifest differs from the fixed overlay')
            for name,row in mapping.items():
                path=regular(root,name)
                with path.open('rb') as stream:
                    if path.stat().st_size != row['size'] or digest(stream) != row['sha256']:
                        raise ValueError('Previously applied payload changed: '+name)
        summary={'ok':True,'mode':'verify-only' if args.verify_only else ('already-applied' if applied else 'apply'),
                 'base_commit':BASE_COMMIT,'overlay_sha256':args.sha256,'overlay_files':len(names),
                 'overlay_uncompressed_bytes':total,'repository_payloads_verified':len(mapping),
                 'old_tracked_files_protected':len(base),'current_translation_unchanged':True}
        if args.verify_only or applied:
            print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0
        # Each file replacement is atomic. The manifest is written last; no
        # receipt is emitted until every validated payload has been installed.
        for info in sorted(infos,key=lambda i:(i.filename==MANIFEST,i.filename)):
            target=root/info.filename; target.parent.mkdir(parents=True,exist_ok=True)
            descriptor,tmp=tempfile.mkstemp(prefix='.archive1-',dir=target.parent)
            try:
                with os.fdopen(descriptor,'wb') as output, archive.open(info) as source:
                    shutil.copyfileobj(source,output); output.flush(); os.fsync(output.fileno())
                os.chmod(tmp,0o755 if (info.external_attr>>16)&0o111 else 0o644)
                os.replace(tmp,target)
            finally:
                if os.path.exists(tmp): os.unlink(tmp)
    summary.update({'release_tag':'v19-archive1-20261125','translation_edition':19,
                    'applied_at_utc':datetime.now(timezone.utc).isoformat(),
                    'scope':'Archive-only historical and Dot supplement; current/EGA_v19 unchanged; no new translation claimed'})
    with receipt_path.open('x',encoding='utf-8') as output:
        output.write(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except (ValueError,KeyError,OSError,zipfile.BadZipFile,subprocess.CalledProcessError) as exc:
        print(str(exc),file=sys.stderr); raise SystemExit(1)
