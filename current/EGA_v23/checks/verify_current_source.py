#!/usr/bin/env python3
"""Check edition 23 inputs, preserved edition-22 sources, and exact flattening.

Byte and wiring checks do not constitute mathematical review. A separate prior
project can be supplied to read its actual files in addition to pinned hashes.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = 'a1e4d5b58aee845096b7bae25e7e1e7e9482d7fa'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--reference-project',type=Path)
args=parser.parse_args()
BASE=(args.reference_project or ROOT.parent/'EGA_v22').resolve()
INPUT=re.compile(r'^\s*\\input\{([^}]+)\}\s*(?:%[^\n]*)?$',re.M)
NEW_BOOK=['continuations/v23_section15_setup.tex','continuations/v23_section15_smoothness.tex']
NEW_REPORT=['reports/v23_integration_audit.tex','reports/v23_section15_setup_audit.tex','reports/v23_section15_smoothness_audit.tex']
OLD_INPUT='continuations/v22_section15_inherited.tex'
OLD_LATE='continuations/v_dot_late.tex'
errors,chains,preserved=[],{},[]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def regular(base,name):
    rel=PurePosixPath(name)
    if not name or rel.is_absolute() or '..' in rel.parts or '\\' in name or rel.as_posix()!=name:
        raise ValueError('Unsafe project path: '+str(name))
    p=base/name
    if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(base.resolve()) or any(q.is_symlink() for q in p.parents if q!=base):
        raise ValueError('Missing or unsafe regular file: '+name)
    return p

def walk(base,name,ancestors=()):
    if name in ancestors: raise ValueError('Cyclic TeX input: '+name)
    text=regular(base,name).read_text(encoding='utf-8')
    result=[name]
    for item in INPUT.findall(text):
        result.extend(walk(base,item if Path(item).suffix else item+'.tex',ancestors+(name,)))
    return result

baseline=None
reference_read=False
try:
    baseline=json.loads(regular(ROOT,'checks/inherited_source_baseline.json').read_text())
    if baseline.get('baseline_edition')!=22 or baseline.get('target_edition')!=23 or baseline.get('baseline_commit')!=BASE_COMMIT:
        raise ValueError('Wrong source baseline edition or commit')
    plan=json.loads(regular(ROOT,'checks/edition_plan.json').read_text())
    if (plan.get('schema_version')!=2 or plan.get('edition')!=23 or plan.get('baseline_commit')!=BASE_COMMIT
            or plan.get('new_book_modules')!=NEW_BOOK or plan.get('new_report_modules')!=NEW_REPORT
            or plan.get('replaced_old_input')!=OLD_INPUT):
        raise ValueError('New module interface does not match the reviewed edition-23 plan')
    rows=baseline['files']; names=[r['path'] for r in rows]
    if not rows or len(names)!=len(set(names)): raise ValueError('Invalid inherited inventory')
    reference_read=BASE.is_dir()
    if reference_read:
        actual={p.relative_to(BASE).as_posix() for d in baseline['directories'] for p in (BASE/d).rglob('*.tex') if p.is_file()}
        if actual!=set(names): errors.append({'baseline_inventory_changed':{'missing':sorted(set(names)-actual),'extra':sorted(actual-set(names))}})
    for row in rows:
        name=row['path']; equal=False
        try:
            if reference_read:
                before=regular(BASE,name)
                if before.stat().st_size!=row['size'] or sha(before)!=row['sha256']:
                    errors.append('Actual previous source differs from pinned baseline: '+name)
            now=regular(ROOT,name)
            equal=now.stat().st_size==row['size'] and sha(now)==row['sha256']
        except (OSError,ValueError) as exc: errors.append(str(exc))
        preserved.append({'path':name,'unchanged':equal,'baseline_sha256':row['sha256']})
        if not equal: errors.append('Inherited source changed or missing: '+name)
    for entry in ('main.tex','report.tex'):
        if reference_read and walk(BASE,entry)!=baseline['input_chains'][entry]:
            errors.append('Actual previous input chain differs: '+entry)
    if sha(regular(ROOT,'preamble.tex'))!=baseline['preamble_sha256']:
        errors.append('Inherited preamble changed')
except (OSError,ValueError,KeyError,TypeError) as exc:
    errors.append('Baseline validation failed: '+str(exc)); baseline=None

retained_project_files=0
try:
    retained=json.loads(regular(ROOT,'recollation/legacy_v22/RETAINED_PROJECT_FILES.json').read_text())
    if (retained.get('baseline_edition')!=22 or retained.get('target_edition')!=23
            or retained.get('baseline_commit')!=BASE_COMMIT):
        raise ValueError('Wrong prior-project retention map')
    original_names=[r['original_path'] for r in retained['files']]
    if len(original_names)!=len(set(original_names)) or len(original_names)!=retained['file_count']:
        raise ValueError('Duplicate or inconsistent prior-project retention map')
    for row in retained['files']:
        saved=regular(ROOT,row['retained_path'])
        if saved.stat().st_size!=row['bytes'] or sha(saved)!=row['sha256']:
            raise ValueError('Prior-project retained bytes differ: '+row['original_path'])
        if reference_read:
            original=regular(BASE,row['original_path'])
            if original.stat().st_size!=row['bytes'] or sha(original)!=row['sha256']:
                raise ValueError('Prior-project actual baseline differs: '+row['original_path'])
        retained_project_files+=1
except (OSError,ValueError,KeyError,TypeError) as exc:
    errors.append('Prior-project preservation: '+str(exc))

for entry in ('main.tex','report.tex'):
    try:
        chains[entry]=walk(ROOT,entry)
        duplicates={k:v for k,v in Counter(chains[entry]).items() if v!=1}
        if duplicates: errors.append({'duplicate_input':entry,'paths':duplicates})
    except (OSError,ValueError) as exc: errors.append('Input traversal: '+str(exc))

if baseline:
    prior_book=baseline['input_chains']['main.tex']; prior_report=baseline['input_chains']['report.tex']
    if prior_book.count(OLD_INPUT)!=1: errors.append('Prior book must have exactly one old section15 input')
    expected=[]
    for name in prior_book: expected.extend(NEW_BOOK if name==OLD_INPUT else [name])
    if chains.get('main.tex')!=expected: errors.append('Book input chain differs from exact section15 substitution')
    insertion=next((i for i,n in enumerate(prior_report) if n.startswith('reports/')),None)
    if insertion is None: errors.append('No prior report insertion boundary')
    elif chains.get('report.tex')!=prior_report[:insertion]+NEW_REPORT+prior_report[insertion:]:
        errors.append('Report input chain differs from new audits plus unchanged historical sequence')

book=chains.get('main.tex',[])
for number in range(69,109):
    name=f'continuations/v18_batch{number:03d}.tex'
    if book.count(name)!=1: errors.append('Dot input missing or duplicated: '+name)
for name in [OLD_INPUT,OLD_LATE,'continuations/v20_section13_inherited.tex']:
    if name in book: errors.append('Inactive original input was reintroduced: '+name)
for name in NEW_BOOK+NEW_REPORT:
    try:
        if not regular(ROOT,name).read_text().strip(): errors.append('Empty new module: '+name)
    except (OSError,ValueError) as exc: errors.append(str(exc))

old_late,old14,inherited15,old13=b'',b'',b'',b''
remainder_equal=concatenation_equal=False
try:
    if not baseline: raise ValueError('Validated baseline required')
    split=baseline['section14_15_split']
    if split['old_path']!=OLD_LATE or split['inherited_section15_path']!=OLD_INPUT: raise ValueError('Wrong historical split paths')
    old_late=regular(ROOT,OLD_LATE).read_bytes()
    old14=regular(ROOT,split['archived_section14_path']).read_bytes()
    inherited15=regular(ROOT,OLD_INPUT).read_bytes()
    if regular(ROOT,split['archived_whole_path']).read_bytes()!=old_late: raise ValueError('Historical whole-file archive differs')
    marker=split['boundary_marker'].encode()
    if old_late.count(marker)!=1 or old_late.index(marker)!=split['boundary_byte_offset']: raise ValueError('Original heading boundary changed')
    for data,prefix in ((old_late,'whole'),(old14,'section14'),(inherited15,'section15')):
        if len(data)!=split[prefix+'_bytes'] or hashlib.sha256(data).hexdigest()!=split[prefix+'_sha256']: raise ValueError('Original preserved slice differs: '+prefix)
    remainder_equal=inherited15==old_late[split['boundary_byte_offset']:]
    concatenation_equal=old14+inherited15==old_late
    if not remainder_equal or not concatenation_equal: raise ValueError('Historical slices no longer reconstruct original')
    old13=regular(ROOT,'continuations/v20_section13_inherited.tex').read_bytes()
    if old13!=regular(ROOT,'recollation/legacy_v20/v20_section13_inherited.tex').read_bytes(): raise ValueError('Old section13 archive differs')
except (OSError,ValueError,KeyError,TypeError) as exc: errors.append('Historical preservation: '+str(exc))

try:
    spec=importlib.util.spec_from_file_location('flatten',regular(ROOT,'flatten_sources.py'))
    flat=importlib.util.module_from_spec(spec); spec.loader.exec_module(flat)
    for entry,single in (('main.tex','single.tex'),('report.tex','report_single.tex')):
        text=regular(ROOT,single).read_text()
        if flat.expand(ROOT/entry)!=text: errors.append('Standalone source differs from exact current expansion: '+single)
        if re.search(r'\\(?:input|include)\{',text): errors.append('Standalone source still contains input: '+single)
    pre=regular(ROOT,'preamble.tex').read_text()
    if '\\documentclass[UTF8,a4paper]{ctexbook}' not in pre: errors.append('Unexpected document class')
    for command in (r'\\setCJKmainfont',r'\\setmainfont',r'\\geometry',r'\\usepackage(?:\[[^]]*\])?\{geometry\}'):
        if re.search(command,pre): errors.append('Unexpected font or geometry override: '+command)
except (OSError,ValueError,ImportError) as exc: errors.append('Flattening/preamble validation: '+str(exc))

notes=[]; audits=[]
for name in NEW_BOOK:
    path=ROOT/name
    if path.is_file(): notes+=re.findall(r'\\cmt\{([^}]+)\}',path.read_text())
for name in NEW_REPORT:
    path=ROOT/name
    if path.is_file(): audits+=re.findall(r'\\audit\{([^}]+)\}',path.read_text())
for kind,ids in [('notes',notes),('audits',audits)]:
    duplicate={k:v for k,v in Counter(ids).items() if v>1}
    if duplicate: errors.append({'duplicate_current_'+kind:duplicate})
active_hashes={}; single_hashes={}
try:
    active_hashes={name:sha(regular(ROOT,name)) for name in sorted(set(sum(chains.values(),[])))}
    single_hashes={name:sha(regular(ROOT,name)) for name in ('single.tex','report_single.tex')}
except (OSError,ValueError) as exc: errors.append('Source binding: '+str(exc))
result={'edition':23,'pass':not errors,'errors':errors,'source_records':len(active_hashes),
        'input_chains':chains,'active_source_sha256':active_hashes,'standalone_source_sha256':single_hashes,
        'new_section15_modules':NEW_BOOK,'new_report_modules':NEW_REPORT,
        'inherited_source_files_unchanged':sum(r['unchanged'] for r in preserved),
        'inherited_source_files_expected':len(preserved),'preserved_source_records':preserved,
        'dot_modules_input_once':sum(book.count(f'continuations/v18_batch{n:03d}.tex')==1 for n in range(69,109)),
        'baseline_commit':BASE_COMMIT,'baseline_comparison_mode':'actual_previous_project_and_recorded_hashes' if reference_read else 'recorded_baseline_hashes_only',
        'previous_project_actually_read_this_run':reference_read,'previous_project_files_preserved':retained_project_files,
        'section13_preserved_original_bytes':len(old13),'original_v_dot_late_bytes':len(old_late),
        'section14_preserved_original_bytes':len(old14),'section15_inherited_bytes':len(inherited15),
        'section15_remainder_byte_identical':remainder_equal,'section14_15_concatenation_matches_original':concatenation_equal,
        'current_section15_footnotes':len(notes),'current_audit_items':len(audits),
        'scope':'Actual preserved bytes, current wiring, default preamble and exact single-source expansion; no mathematical-completeness claim'}
(ROOT/'checks/current_structure_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('input_chains','preserved_source_records','active_source_sha256','standalone_source_sha256')},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
