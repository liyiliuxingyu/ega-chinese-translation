#!/usr/bin/env python3
"""Export an archive-only v19 supplement without rebuilding translation PDFs."""
from __future__ import annotations
import argparse, hashlib, json, shutil, stat, subprocess, zipfile
from pathlib import Path, PurePosixPath

BASE_COMMIT='4daf708a87069e2a6e28c22a29d3e3af26880f0b'
WORKFLOW='.github/workflows/publish-archive-supplement-20261125.yml'
RECEIPT='ARCHIVE_SUPPLEMENT_IMPORT.json'
MANIFEST='REPOSITORY_MANIFEST.json'
ROOT_UPDATES={'README.md','AGENTS.md','CONTINUE_HERE.md',MANIFEST}
SNAPSHOT='snapshots/20261125-archive1/'
SUPPLEMENT='archive_supplement_20261125/'
NEW_TOOLS={'tools/apply_archive1_update.py','tools/package_archive1.py'}
PUBLICATION_METADATA={'.github/workflows/import-20261124.yml','IMPORT_RECEIPT.json',
    '.github/workflows/publish-edition18.yml','EDITION_18_IMPORT.json',
    '.github/workflows/publish-edition19.yml','EDITION_19_IMPORT.json',WORKFLOW,RECEIPT}

def safe_name(name):
    if not isinstance(name,str) or any(c in name for c in ('\\','\0','\r','\n')): return False
    p=PurePosixPath(name)
    return bool(name) and p.as_posix()==name and not p.is_absolute() and '..' not in p.parts and all(x.lower()!='.git' for x in p.parts)

def safe_file(root,name):
    if not safe_name(name): raise ValueError('Unsafe file name: '+repr(name))
    p=root/name
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root) or any(x.is_symlink() for x in p.parents if x!=root):
        raise ValueError('Not a safe regular file: '+name)
    return p

def sha(path):
    with path.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

def tree(root,ref):
    result={}
    for record in subprocess.check_output(['git','-C',str(root),'ls-tree','-r','-z',ref]).split(b'\0'):
        if not record: continue
        meta,name=record.split(b'\t',1); mode,kind,digest=meta.decode('ascii').split(); name=name.decode('utf-8')
        if not safe_name(name) or kind!='blob' or mode not in ('100644','100755'): raise ValueError('Unsupported tracked file: '+name)
        result[name]=(mode,kind,digest)
    return result

def pack(root,records,target):
    if len({row['path'] for row in records})!=len(records): raise ValueError('Duplicate ZIP paths')
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as archive:
        for row in sorted(records,key=lambda r:r['path']):
            path=safe_file(root,row['path'])
            info=zipfile.ZipInfo(row['path'],(2026,11,25,0,0,0)); info.create_system=3; info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(stat.S_IFREG|(0o755 if path.stat().st_mode&0o111 else 0o644))<<16
            with path.open('rb') as source,archive.open(info,'w',force_zip64=True) as output: shutil.copyfileobj(source,output)
    # The expected hashes come from the independently checked repository manifest;
    # every stored ZIP member is re-read and compared against those exact bytes.
    with zipfile.ZipFile(target) as archive:
        infos=archive.infolist()
        if len(infos)!=len(records) or {i.filename for i in infos}!={r['path'] for r in records}: raise ValueError('ZIP member set mismatch')
        for row in records:
            info=archive.getinfo(row['path'])
            with archive.open(info) as stream:
                if info.file_size!=row['size'] or hashlib.file_digest(stream,'sha256').hexdigest()!=row['sha256']:
                    raise ValueError('Re-read ZIP member hash mismatch: '+row['path'])
    return {'file':target.name,'size':target.stat().st_size,'sha256':sha(target),'members':len(records),
            'uncompressed_bytes':sum(r['size'] for r in records),'all_member_hashes_verified':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--verify-only',action='store_true',help='Check preservation and every package input without creating archives')
    args=parser.parse_args(); root=args.root.resolve(); output=args.output.resolve()
    if output==root or output.is_relative_to(root): raise ValueError('Export directory must be outside the repository')
    if subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=all']): raise ValueError('Package only a clean committed checkout')
    subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',BASE_COMMIT,'HEAD'],check=True)
    old=tree(root,BASE_COMMIT); current=tree(root,'HEAD')
    for name,identity in old.items():
        if name not in current: raise ValueError('Old tracked file removed: '+name)
        if name not in ROOT_UPDATES and current[name]!=identity: raise ValueError('Protected old tracked bytes or mode changed: '+name)
    for name in set(current)-set(old):
        if not (name in NEW_TOOLS|{WORKFLOW,RECEIPT} or name.startswith((SUPPLEMENT,SNAPSHOT))):
            raise ValueError('Unexpected added tracked file: '+name)
    for name in ROOT_UPDATES:
        if current.get(SNAPSHOT+name)!=old[name]: raise ValueError('Old root snapshot is not byte/mode identical: '+name)
    manifest=json.loads(safe_file(root,MANIFEST).read_text())
    metadata=manifest.get('allowed_publication_metadata')
    if not isinstance(metadata,list) or len(metadata)!=len(PUBLICATION_METADATA) or set(metadata)!=PUBLICATION_METADATA:
        raise ValueError('Unexpected publication metadata set')
    rows=manifest['files']; names=[r['path'] for r in rows]
    if len(names)!=len(set(names)) or set(names)&(PUBLICATION_METADATA|{MANIFEST}): raise ValueError('Duplicate or excluded manifest path')
    if set(names)|PUBLICATION_METADATA|{MANIFEST}!=set(current): raise ValueError('Manifest does not exactly cover the committed tree')
    for row in rows:
        path=safe_file(root,row['path'])
        if type(row.get('size')) is not int or path.stat().st_size!=row['size'] or sha(path)!=row['sha256']:
            raise ValueError('Repository payload mismatch: '+row['path'])
    supplement=[r for r in rows if r['path'].startswith(SUPPLEMENT)]
    if not supplement: raise ValueError('No supplemental archive payload')
    exports={SUPPLEMENT+'AUDIT_REPORT.md':'EGA-upload-audit-20261125.md',
             SUPPLEMENT+'AUDIT_SUMMARY.json':'EGA-upload-audit-20261125.json'}
    if not set(exports)<=set(names): raise ValueError('Required audit reports are missing')
    extra_rows=[]
    for name in sorted(PUBLICATION_METADATA|{MANIFEST}):
        path=safe_file(root,name); extra_rows.append({'path':name,'size':path.stat().st_size,'sha256':sha(path)})
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    receipt=json.loads(safe_file(root,RECEIPT).read_text())
    if receipt.get('base_commit')!=BASE_COMMIT or receipt.get('translation_edition')!=19 or receipt.get('release_tag')!='v19-archive1-20261125':
        raise ValueError('Import receipt does not describe this archive-only supplement')
    preliminary={'pass':True,'base_commit':BASE_COMMIT,'publication_commit':commit,'translation_edition':19,
        'current_project_unchanged':True,'repository_payloads_verified':len(rows),
        'full_archive_members':len(rows)+len(extra_rows),'supplement_archive_members':len(supplement)}
    if args.verify_only:
        print(json.dumps(preliminary,ensure_ascii=False,indent=2)); return
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()): raise ValueError('Export directory must be empty')
    bundles=[pack(root,rows+extra_rows,output/'EGA-all-projects-with-Dot-v19-archive1-20261125.zip'),
             pack(root,supplement,output/'EGA-history-and-Dot-supplement-20261125.zip')]
    export_records=[]
    for source,target in exports.items():
        shutil.copy2(safe_file(root,source),output/target)
        row=next(r for r in rows if r['path']==source); local=output/target
        if local.stat().st_size!=row['size'] or sha(local)!=row['sha256']: raise ValueError('Report export mismatch')
        export_records.append({'file':target,'size':local.stat().st_size,'sha256':sha(local)})
    result={**preliminary,'release_tag':'v19-archive1-20261125','date':'2026-11-25',
        'repository_manifest_sha256':sha(root/MANIFEST),'bundles':bundles,'exports':export_records,
        'supplement_scope':'Only archive_supplement_20261125/ is in the supplement ZIP; obtain the full ZIP for a complete continuation workspace.',
        'scope':'Archive completeness supplement and reproducible evidence; no new translation or mathematical certification claimed'}
    (output/'PACKAGE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    sums=''.join(f'{sha(path)}  {path.name}\n' for path in sorted(output.iterdir()) if path.is_file())
    (output/'SHA256SUMS.txt').write_text(sums)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
