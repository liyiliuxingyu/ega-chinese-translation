#!/usr/bin/env python3
"""Read-only content audit; writes evidence only beside this script."""
from pathlib import Path, PurePosixPath
from collections import defaultdict, Counter
import datetime, hashlib, json, re, zipfile, zlib

ROOT = Path('/workspace/scratch/a886fd56dd2f')
OUT = ROOT / 'integration_20261121'
BASE = ROOT / 'restored_20261121/baseline/EGA_v17_handover'
NEW = ROOT / 'restored_20261121/latest/EGA_v17_V_supplement_III'
OLDZIP = ROOT / 'recovered_20261121/baseline/EGA中文译校_第十七版_完整续作工程包.zip'
PREFIX = '01_project/EGA_v17/'

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def put(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def safe_rel(p):
    q = PurePosixPath(p)
    return not q.is_absolute() and '..' not in q.parts and '\\' not in p

def inv(root):
    res = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError(f'Symlink not accepted: {p}')
        if p.is_file():
            res[p.relative_to(root).as_posix()] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
    return res

def dist(ii):
    d = defaultdict(lambda: {'files': 0, 'bytes': 0})
    for p, v in ii.items():
        k = p.split('/')[0] if '/' in p else '[root]'
        d[k]['files'] += 1
        d[k]['bytes'] += v['bytes']
    return dict(sorted(d.items()))

def dup_groups(ii):
    g = defaultdict(list)
    for p, v in ii.items():
        g[v['sha256']].append(p)
    rows = []
    for h, paths in g.items():
        if len(paths) > 1:
            size = ii[paths[0]]['bytes']
            rows.append({'sha256': h, 'bytes_each': size, 'copies': len(paths),
                         'raw_bytes_savable': size * (len(paths)-1), 'paths': paths})
    rows.sort(key=lambda x: x['raw_bytes_savable'], reverse=True)
    return rows

bi, ni = inv(BASE), inv(NEW)
old_m = json.loads((BASE / 'MANIFEST.json').read_text())
old_errors = []
for row in old_m['files']:
    p = row['path']
    if not safe_rel(p) or p not in bi or any(bi[p][k] != row[k] for k in ['bytes', 'sha256']):
        old_errors.append(p)
expected = {r['path'] for r in old_m['files']} | {'MANIFEST.json', 'SHA256SUMS.txt'}
old_errors.extend('extra:' + p for p in set(bi)-expected)
old_errors.extend('missing:' + p for p in expected-set(bi))
old_sums = {}
for line in (BASE / 'SHA256SUMS.txt').read_text().splitlines():
    h, p = line.split('  ', 1)
    if not safe_rel(p) or p not in bi or bi[p]['sha256'] != h:
        old_errors.append('sha256sums:' + p)
    if p in old_sums:
        old_errors.append('sha256sums_duplicate:' + p)
    old_sums[p] = h
if set(old_sums) != {r['path'] for r in old_m['files']} | {'MANIFEST.json'}:
    old_errors.append('sha256sums_inventory_mismatch')

latest_sums_errors = []
latest_sums = {}
for line in (NEW / 'SHA256SUMS.txt').read_text().splitlines():
    h, p = line.split('  ', 1)
    if not safe_rel(p) or p not in ni or ni[p]['sha256'] != h:
        latest_sums_errors.append(p)
    if p in latest_sums:
        latest_sums_errors.append('duplicate:' + p)
    latest_sums[p] = h
latest_unlisted = sorted(set(ni)-set(latest_sums)-{'SHA256SUMS.txt'})

migration = json.loads((BASE / '01_project/EGA_v17/checks/v16_complete_migration.json').read_text())
migration_rows = []
for row in migration['mapping']:
    p = row['packaged_path']
    ok = safe_rel(p) and p in bi and all(bi[p][k] == row[k] for k in ['bytes', 'sha256'])
    migration_rows.append({**row, 'verified_now': ok})
put('v16_435_mapping_reverified.json', migration_rows)

source_manifest = json.loads((BASE / '07_integration_records/integration/source_corpus_manifest.json').read_text())
sources = []
import fitz
for row in source_manifest['source_files']:
    p = '03_sources/' + row['suggested_stable_filename']
    actual = bi.get(p)
    check = {'id': row['id'], 'path': p, 'bytes': actual['bytes'] if actual else None,
             'sha256': actual['sha256'] if actual else None,
             'matches_source_manifest': bool(actual) and all(actual[k] == row[k] for k in ['bytes', 'sha256']),
             'same_bytes_in_latest': actual == ni.get(p), 'format': row['format']}
    if row['format'] == 'PDF':
        with fitz.open(BASE / p) as doc:
            check['pdf_pages_measured'] = len(doc)
        check['pdf_page_count_matches'] = check['pdf_pages_measured'] == row.get('pdf_page_count')
    sources.append(check)

dots = json.loads((BASE / '05_Dot/DOT_BATCHES.json').read_text())
dot_rows = []
all_dot_engineering = set()
for row in dots['batches']:
    p = row['packaged_tex_path']
    checks = {'order': row['order'], 'path': p, 'sha256': bi[p]['sha256'] if p in bi else None,
              'tex_sha_matches': p in bi and bi[p]['sha256'] == row['source_tex_sha256'],
              'integration_treatment': row['integration_treatment'],
              'current_project_input': row['current_project_input'],
              'input_exists_in_latest': ('project/' + row['current_project_input']) in ni,
              'missing_engineering_files': [s for s in row['extracted_engineering_files'] if s not in bi]}
    dot_rows.append(checks)
    all_dot_engineering.update(row['extracted_engineering_files'])
archives = []
for row in dots['original_archives']:
    p = row['packaged_path']
    with zipfile.ZipFile(BASE / p) as z:
        bad = z.testzip()
        entries = len(z.infolist())
    archives.append({'path': p, **bi[p], 'expected_bytes_sha_match':
                     all(bi[p][k] == row[k] for k in ['bytes','sha256']),
                     'zip_entries': entries, 'crc_pass': bad is None, 'bad_crc_member': bad})

op = {k[len(PREFIX):]: v for k, v in bi.items() if k.startswith(PREFIX)}
np = {k[8:]: v for k, v in ni.items() if k.startswith('project/')}
unchanged = [p for p in op if op[p] == np.get(p)]
changed = [p for p in op if p in np and op[p] != np[p]]
missing_at_path = [p for p in op if p not in np]
relocated, absent = [], []
for p in missing_at_path:
    target = 'checks/v17-baseline/' + p[len('checks/'):] if p.startswith('checks/') else None
    if target in np and np[target] == op[p]:
        relocated.append({'old': p, 'new': target, **op[p]})
    else:
        absent.append(p)
new_at_path = [p for p in np if p not in op]
relocated_targets = {r['new'] for r in relocated}
genuine_new = [p for p in new_at_path if p not in relocated_targets]

# Every old file gets a currently existing byte-identical referent and a proposed
# destination. No proposed final destination is claimed to have been materialized.
old_to_current = []
plan = {}
relocate_map = {r['old']: r['new'] for r in relocated}
for p, v in bi.items():
    actual_root, actual_path = 'baseline', p
    if p.startswith(PREFIX):
        rel = p[len(PREFIX):]
        if rel in unchanged:
            target = p
            actual_root, actual_path = 'latest', 'project/' + rel
            action = 'reuse_identical_current_project'
        elif rel in relocate_map:
            target = PREFIX + relocate_map[rel]
            actual_root, actual_path = 'latest', 'project/' + relocate_map[rel]
            action = 'reuse_identical_relocated_historical_check'
        else:
            target = '04_history/v17_before_supplement/' + rel
            action = 'preserve_changed_or_missing_old_project_file'
    elif '/' not in p or p.startswith('00_START_HERE/'):
        target = '04_history/v17_handover_before_supplement/' + p
        action = 'archive_old_package_entry_or_manifest'
    elif p.startswith('02_deliverables/'):
        target = '04_history/v17_outputs/' + p[len('02_deliverables/'):]
        action = 'archive_old_named_deliverable'
    else:
        target = p
        action = 'retain_existing_path'
        if p in ni and ni[p] == v:
            actual_root, actual_path = 'latest', p
    row = {'old_path': p, **v, 'existing_source_tree': actual_root,
           'existing_source_path': actual_path,
           'existing_absolute_path': str((NEW if actual_root=='latest' else BASE) / actual_path),
           'proposed_final_path': target, 'proposed_action': action,
           'byte_match_verified_now': (ni if actual_root=='latest' else bi)[actual_path] == v}
    old_to_current.append(row)
    if target in plan and plan[target]['sha256'] != v['sha256']:
        raise ValueError('Proposed collision: ' + target)
    plan[target] = {**v, 'existing_absolute_path': row['existing_absolute_path']}

for p, v in ni.items():
    if p.startswith('project/'):
        target = PREFIX + p[len('project/'):]
    elif p.startswith('03_sources/') or p.startswith('05_Dot_new_batches/'):
        target = p
    else:
        target = '04_history/supplement_III_original_package/' + p
    if target in plan and plan[target]['sha256'] != v['sha256']:
        raise ValueError('Proposed collision with latest: ' + target)
    plan[target] = {**v, 'existing_absolute_path': str(NEW / p)}
put('baseline_all_1827_path_mapping.json', {'status': 'proposed final layout; existing byte sources verified; no final package was written by this audit', 'files': old_to_current})
put('proposed_merge_inventory.json', plan)

base_dups = dup_groups(bi)
plan_dups = dup_groups(plan)
put('byte_identical_duplicates.json', {'baseline': base_dups, 'proposed_merge': plan_dups})

# Compute DEFLATE level 9 payload sizes using each unique file's real bytes.
# This is a reproducible estimate, not a claim that a final ZIP exists.
by_sha = {}
for p, v in plan.items():
    by_sha.setdefault(v['sha256'], v)
compressed = {}
for h, v in by_sha.items():
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    total = 0
    with Path(v['existing_absolute_path']).open('rb') as f:
        while chunk := f.read(1 << 20):
            total += len(compressor.compress(chunk))
    total += len(compressor.flush())
    compressed[h] = total

def estimate(ii, unique=False):
    rows = list(ii.items())
    if unique:
        rows = list({v['sha256']: (p,v) for p,v in reversed(rows)}.values())
    payload = sum(compressed[v['sha256']] for p,v in rows)
    overhead = sum(76 + 2*len(p.encode('utf-8')) for p,v in rows) + 22
    return {'files_or_unique_blobs': len(rows), 'uncompressed_bytes': sum(v['bytes'] for p,v in rows),
            'raw_deflate9_payload_bytes': payload, 'estimated_zip_headers_bytes': overhead,
            'estimated_zip_bytes': payload + overhead}

old_compress_map = {}
with zipfile.ZipFile(OLDZIP) as z:
    for zi in z.infolist():
        rel = zi.filename.split('/',1)[1]
        old_compress_map[rel] = zi.compress_size

for row in base_dups:
    sizes = [old_compress_map[p] for p in row['paths']]
    row['compressed_payload_savable_in_existing_zip'] = sum(sizes)-min(sizes)
put('byte_identical_duplicates.json', {'baseline': base_dups, 'proposed_merge': plan_dups})

# Keep every current project's physical path; deduplicate only additional
# archival paths by verified content references. This is a proposal only.
strict_current = {p:v for p,v in plan.items() if p.startswith(PREFIX)}
seen = {v['sha256'] for v in strict_current.values()}
historical_dedup_plan = dict(strict_current)
canonical_by_sha = {}
for p,v in strict_current.items():
    canonical_by_sha.setdefault(v['sha256'],p)
dedup_aliases = []
for p,v in plan.items():
    if p.startswith(PREFIX):
        continue
    if v['sha256'] not in seen:
        historical_dedup_plan[p] = v
        seen.add(v['sha256'])
        canonical_by_sha[v['sha256']] = p
    else:
        dedup_aliases.append({'logical_path':p,'canonical_path':canonical_by_sha[v['sha256']],
                              'bytes':v['bytes'],'sha256':v['sha256']})
put('dedup_candidates_preserve_active_project.json',{
    'status':'Proposal only; no source file deleted or final package created',
    'physical_file_count':len(historical_dedup_plan),'logical_file_count':len(plan),
    'physical_files':historical_dedup_plan,'aliases_requiring_restoration':dedup_aliases})

documents = []
for tree, root, path in [('baseline',BASE,'01_project/EGA_v17/main.pdf'),('baseline',BASE,'01_project/EGA_v17/report.pdf'),('latest',NEW,'project/main.pdf'),('latest',NEW,'project/report.pdf')]:
    with fitz.open(root / path) as doc:
        documents.append({'tree':tree,'path':path,'pages_measured':len(doc),'sha256':sha(root/path)})

vendor_old = {k:v for k,v in op.items() if k.startswith('vendor/')}
vendor_bad = [k for k,v in vendor_old.items() if np.get(k) != v]
build_files = ['build.sh','build_supplement_III.sh','flatten_sources.py','scripts/tex_environment.sh','preamble.tex']
subtree_comparison = {}
for tree in ['text','continuations','backmatter','reports','vendor']:
    old = {k:v for k,v in op.items() if k.startswith(tree + '/')}
    bad = [k for k,v in old.items() if np.get(k) != v]
    subtree_comparison[tree] = {'old_count':len(old),'identical_in_latest':len(old)-len(bad),'changed_or_missing':bad}
with fitz.open(NEW/'03_sources/EGA5_francais.pdf') as french:
    french_pages = len(french)

issues = [
    {'severity':'integration_requirement','message':'The third-supplement package is not a substitute for the complete old archive: it omits old 04_history, 05_Dot and 07_integration_records trees. Preserve these from the verified baseline.'},
    {'severity':'provenance_requirement','message':'15 current-project files changed. Preserve their old byte versions before replacing the active project.'},
    {'severity':'historical_routing','message':'68 checks files moved byte-identically to checks/v17-baseline. Do not report these as lost and do not run old validators as if they target the new active project.'},
    {'severity':'noncritical_generated_cache','message':'Only __pycache__/flatten_sources.cpython-312.pyc from the old project has no identical third-supplement counterpart at the expected relocation. It remains intact in the recovered baseline and is mapped to historical preservation; it is not source or a build dependency.'},
    {'severity':'metadata_requirement','message':'Old entry points, MANIFEST and SHA256SUMS describe old releases. Archive them and generate one authoritative new entry/manifest after merging.'},
    {'severity':'scope_limit','message':'This audit checks content preservation, inventories, checksums and file structure; no mathematical proof was reassessed and no TeX compilation was run.'},
]

summary = {
    'audit_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'audit_script': str(OUT/'run_baseline_audit.py'),
    'baseline_root': str(BASE), 'latest_root': str(NEW),
    'baseline_zip': {'path':str(OLDZIP),'bytes':OLDZIP.stat().st_size,'sha256':sha(OLDZIP),
                     'expected_sha256':'f11fa64ad6c3632b09b7379abb99b01b9b72f84cbf65e730d1e74319585295e8',
                     'extraction_record':'baseline_extraction.json'},
    'baseline_manifest': {'pass':not old_errors,'manifest_entries':len(old_m['files']),
                          'all_regular_files':len(bi),'uncompressed_bytes':sum(v['bytes'] for v in bi.values()),
                          'manifest_sha256':bi['MANIFEST.json']['sha256'],'problems':old_errors},
    'latest_checksums': {'pass':not latest_sums_errors and not latest_unlisted,
                         'checksum_entries':len(latest_sums),'regular_files':len(ni),
                         'unlisted_files':latest_unlisted,'problems':latest_sums_errors},
    'historical_435': {'mapping_entries':len(migration_rows),'unique_original_paths':len({r['original_path'] for r in migration_rows}),
                       'unique_packaged_paths':len({r['packaged_path'] for r in migration_rows}),
                       'verified_now':sum(r['verified_now'] for r in migration_rows),
                       'problems':[r for r in migration_rows if not r['verified_now']],
                       'detail':'v16_435_mapping_reverified.json',
                       'scope':'Each mapped payload verified now against its recorded size and SHA; original v16 outer archive not downloaded or re-created by this audit.'},
    'original_sources':sources,
    'new_source':{'path':'03_sources/EGA5_francais.pdf',**ni['03_sources/EGA5_francais.pdf'],'pdf_pages_measured':french_pages},
    'dot_56': {'expected':dots['actual_source_batches'],'actual':len(dot_rows),
               'tex_sha_pass':sum(r['tex_sha_matches'] for r in dot_rows),
               'treatment_counts':dict(Counter(r['integration_treatment'] for r in dot_rows)),
               'listed_engineering_file_count':len(all_dot_engineering),
               'actual_batch_file_count':sum(p.startswith('05_Dot/batches/') for p in bi),
               'engineering_missing':[{'order':r['order'],'missing':r['missing_engineering_files']} for r in dot_rows if r['missing_engineering_files']],
               'archives':archives,'batches':dot_rows},
    'directory_sizes':{'baseline':dist(bi),'latest':dist(ni)},
    'project_comparison': {'baseline_files':len(op),'latest_files':len(np),'unchanged_same_path':len(unchanged),
                           'changed_same_path':len(changed),'moved_identical':len(relocated),'not_in_latest':len(absent),
                           'genuinely_new_paths':len(genuine_new),'changed_paths':changed,'relocated':relocated,
                           'absent_paths':absent,'new_paths':genuine_new,
                           'old_modified_or_absent_bytes':sum(op[p]['bytes'] for p in changed+absent)},
    'project_subtree_comparison':subtree_comparison,
    'build_dependencies': {'old_vendor_files':len(vendor_old),'old_vendor_bytes':sum(v['bytes'] for v in vendor_old.values()),
                           'all_old_vendor_files_same_in_latest':not vendor_bad,'changed_or_missing_vendor':vendor_bad,
                           'latest_build_files':{p:p in np for p in build_files},
                           'engine_bundled':False,'build_not_run':True,
                           'note':'Sourceable TeX-tree setup and open font/package files are preserved. A compatible external XeLaTeX installation remains required; this audit does not revalidate compilation.'},
    'documents_measured':documents,
    'latest_handover_state':json.loads((NEW/'project/HANDOVER_STATE.json').read_text()),
    'preservation_mapping': {'old_file_count':len(old_to_current),'verified_existing_byte_sources':sum(r['byte_match_verified_now'] for r in old_to_current),
                             'all_old_payloads_have_proposed_destination':len(old_to_current)==len(bi),
                             'mapping':'baseline_all_1827_path_mapping.json',
                             'status':'Proposal only. No final merged directory or archive was written by this audit.'},
    'size_estimates': {
        'method':'DEFLATE level 9 applied to the actual bytes of each unique file; ZIP estimate adds 30-byte local and 46-byte central headers plus UTF-8 path names and 22-byte EOCD. New manifests, restoration map/scripts and separately copied current named deliverables are not included. Estimates are not a final archive size.',
        'decimal_512MB':512000000,'binary_512MiB':536870912,
        'existing_baseline_zip_bytes':OLDZIP.stat().st_size,
        'baseline_recompressed_all_paths':estimate(bi),
        'baseline_unique_sha_only':estimate(bi,True),
        'baseline_same_sha_raw_saving':sum(r['raw_bytes_savable'] for r in base_dups),
        'baseline_same_sha_existing_zip_payload_saving':sum(r['compressed_payload_savable_in_existing_zip'] for r in base_dups),
        'proposed_merge_all_paths':estimate(plan),
        'proposed_merge_unique_sha_only':estimate(plan,True),
        'proposed_merge_keep_active_project_paths_and_deduplicate_extra_history':estimate(historical_dedup_plan),
        'historical_dedup_requires':'Explicit byte-to-path restoration map and verified restoration script; ordinary ZIP packaging of hard links still stores repeated bytes. No file was deleted here.',
        'duplicate_groups_detail':'byte_identical_duplicates.json',
        'dedup_candidate_mapping':'dedup_candidates_preserve_active_project.json',
        'do_not_drop':'Original ZIP archives have distinct archival bytes even where their members resemble expanded files. They remain in every estimate; no giant old full handover ZIP is nested inside the proposed new one.'},
    'issues_and_limits':issues
}
put('baseline_audit.json',summary)
print(json.dumps({k:summary[k] for k in ['baseline_manifest','latest_checksums','historical_435','project_comparison','build_dependencies','documents_measured','size_estimates']},ensure_ascii=False,indent=2))
