#!/usr/bin/env python3
"""Check edition20 inputs, preservation and independently flattened TeX bytes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / 'EGA_v19'
INPUT = re.compile(r'^\s*\\input\{([^}]+)\}\s*(?:%[^\n]*)?$', re.MULTILINE)
errors = []
chains = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def walk(name, ancestors=()):
    path = ROOT / name
    if name in ancestors or not path.is_file():
        raise ValueError('Missing or cyclic TeX input: ' + name)
    result = [name]
    for item in INPUT.findall(path.read_text()):
        child = item if Path(item).suffix else item + '.tex'
        if not (ROOT/child).resolve().is_relative_to(ROOT):
            raise ValueError('Input escaped project')
        result.extend(walk(child, ancestors+(name,)))
    return result

for entry in ['main.tex', 'report.tex']:
    chains[entry] = walk(entry)
    dup = {k:v for k,v in Counter(chains[entry]).items() if v != 1}
    if dup: errors.append({'duplicate_input': entry, 'paths': dup})
book = chains['main.tex']
modules = ['opening','extensions','degeneracy','families']
expected = ['continuations/v20_section12_'+x+'.tex' for x in modules]
expected += ['continuations/v20_section13_inherited.tex','continuations/v_dot_late.tex']
positions = [book.index(x) for x in expected]
if positions != sorted(positions): errors.append('New and inherited chapters are out of order')
if 'continuations/v_dot_middle.tex' in book: errors.append('Old section12 was duplicated')
for i in range(69,109):
    name=f'continuations/v18_batch{i:03d}.tex'
    if book.count(name)!=1: errors.append('Dot module missing or duplicated: '+name)

preserved=[]
baseline=json.loads((ROOT/'checks/inherited_source_baseline.json').read_text())
reference_read = (BASE/'continuations/v_dot_middle.tex').is_file()
for row in baseline['files']:
    name=row['path']; now=ROOT/name; original=BASE/name
    if reference_read and (not original.is_file() or sha(original)!=row['sha256']):
        errors.append('Available baseline differs from recorded source: '+name)
    equal=now.is_file() and now.stat().st_size==row['size'] and sha(now)==row['sha256']
    preserved.append({'path':name,'unchanged':equal,'baseline_sha256':row['sha256']})
    if not equal: errors.append('Inherited source changed: '+name)
old=(ROOT/'recollation/legacy_v19/v_dot_middle.tex').read_text()
anchor='\\egasection{§13\\quad 初等态射与 M. Artin 定理}'
suffix=anchor+old.split(anchor,1)[1]
if (ROOT/'continuations/v20_section13_inherited.tex').read_text()!=suffix:
    errors.append('Section13 suffix is not byte-exact')
for name in ['v_dot_middle.tex','dot_middle_audit.tex']:
    original=BASE/('continuations' if name.startswith('v_') else 'reports')/name
    if reference_read and (ROOT/'recollation/legacy_v19'/name).read_bytes()!=original.read_bytes():
        errors.append('Legacy snapshot changed: '+name)

spec=importlib.util.spec_from_file_location('flatten',ROOT/'flatten_sources.py')
flat=importlib.util.module_from_spec(spec);spec.loader.exec_module(flat)
for entry,single in [('main.tex','single.tex'),('report.tex','report_single.tex')]:
    if flat.expand(ROOT/entry)!=(ROOT/single).read_text():
        errors.append('Single source does not equal input expansion: '+single)
    if re.search(r'\\(?:input|include)\{',(ROOT/single).read_text()):
        errors.append('Single source has remaining input: '+single)

pre=(ROOT/'preamble.tex').read_text()
if '\\documentclass[UTF8,a4paper]{ctexbook}' not in pre:
    errors.append('Wrong document class')
for command in [r'\\setCJKmainfont',r'\\setmainfont',r'\\geometry',r'\\usepackage(?:\[[^]]*\])?\{geometry\}']:
    if re.search(command,pre): errors.append('Unexpected font or geometry override: '+command)
notes=[]
for name in expected[:4]:
    notes.extend(re.findall(r'\\cmt\{([^}]+)\}',(ROOT/name).read_text()))
duplicates={k:v for k,v in Counter(notes).items() if v>1}
if duplicates: errors.append({'duplicate_current_note_ids':duplicates})

result={'pass':not errors,'errors':errors,'source_records':len(set(sum(chains.values(),[]))),
        'input_chains':chains,'new_section12_modules':expected[:4],
        'inherited_source_files_unchanged':sum(x['unchanged'] for x in preserved),
        'preserved_source_records':preserved,'dot_modules_input_once':40,
        'baseline_comparison_mode': 'actual_previous_project_and_recorded_hashes' if reference_read else 'recorded_baseline_hashes_only',
        'previous_project_actually_read_this_run':reference_read,
        'section13_exact_inherited_bytes':len(suffix.encode()),
        'current_section12_footnotes':len(notes),
        'scope':'File preservation and TeX input consistency, not proof of mathematical completeness'}
(ROOT/'checks/current_structure_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['input_chains','preserved_source_records']},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
