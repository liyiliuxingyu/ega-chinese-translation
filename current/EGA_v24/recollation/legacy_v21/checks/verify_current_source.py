#!/usr/bin/env python3
"""Verify edition 21 inputs, every inherited TeX body and flattened sources.

This checks bytes and source wiring. It makes no mathematical-completeness claim.
Missing new modules or still-inherited single-file outputs fail explicitly.
"""
from collections import Counter
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / 'EGA_v20'
BASE_COMMIT = '99cd048abd72adad984613aaa4f5fef86cd5a6c8'
INPUT = re.compile(r'^\s*\\input\{([^}]+)\}\s*(?:%[^\n]*)?$', re.MULTILINE)
NEW_BOOK = ['continuations/v21_section13_' + part + '.tex'
            for part in ('initial', 'bertini', 'remarks')]
NEW_REPORT = ['reports/v21_integration_audit.tex'] + [
    'reports/v21_section13_' + part + '_audit.tex'
    for part in ('initial', 'bertini', 'remarks')]
OLD_SECTION13 = 'continuations/v20_section13_inherited.tex'
errors, chains, preserved = [], {}, []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regular(base, name):
    rel = PurePosixPath(name)
    if (not name or rel.is_absolute() or '..' in rel.parts or '\\' in name
            or rel.as_posix() != name):
        raise ValueError('Unsafe project path: ' + str(name))
    path = base / name
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(base.resolve())
            or any(p.is_symlink() for p in path.parents if p != base)):
        raise ValueError('Missing or unsafe regular project file: ' + name)
    return path


def walk(base, name, ancestors=()):
    if name in ancestors:
        raise ValueError('Cyclic TeX input: ' + name)
    path = regular(base, name)
    text = path.read_text(encoding='utf-8')
    result = [name]
    for item in INPUT.findall(text):
        child = item if Path(item).suffix else item + '.tex'
        result.extend(walk(base, child, ancestors + (name,)))
    return result


baseline = None
reference_read = False
try:
    baseline = json.loads(regular(ROOT, 'checks/inherited_source_baseline.json').read_text())
    if (baseline.get('baseline_edition') != 20 or baseline.get('target_edition') != 21
            or baseline.get('baseline_commit') != BASE_COMMIT):
        raise ValueError('The source baseline is not the recorded edition-20 baseline for edition 21')
    rows = baseline['files']
    names = [row['path'] for row in rows]
    if not rows or len(names) != len(set(names)):
        raise ValueError('The inherited source baseline is empty or has duplicate paths')
    reference_read = BASE.is_dir()
    if reference_read:
        actual = {p.relative_to(BASE).as_posix()
                  for directory in baseline['directories']
                  for p in (BASE / directory).rglob('*.tex') if p.is_file()}
        if actual != set(names):
            errors.append({'baseline_inventory_changed': {
                'missing': sorted(set(names) - actual), 'extra': sorted(actual - set(names))}})
    for row in rows:
        name = row['path']
        try:
            if reference_read:
                original = regular(BASE, name)
                if original.stat().st_size != row['size'] or sha(original) != row['sha256']:
                    errors.append('Available previous source differs from its recorded baseline: ' + name)
            now = regular(ROOT, name)
            equal = now.stat().st_size == row['size'] and sha(now) == row['sha256']
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            equal = False
        preserved.append({'path': name, 'unchanged': equal, 'baseline_sha256': row['sha256']})
        if not equal:
            errors.append('Inherited source changed or missing: ' + name)
    for entry in ('main.tex', 'report.tex'):
        if reference_read and walk(BASE, entry) != baseline['input_chains'][entry]:
            errors.append('Available previous input chain differs from its recorded baseline: ' + entry)
    if sha(regular(ROOT, 'preamble.tex')) != baseline['preamble_sha256']:
        errors.append('Inherited preamble changed; review before accepting new global macro meanings')
except (OSError, ValueError, KeyError, TypeError) as exc:
    errors.append('Baseline validation failed: ' + str(exc))
    baseline = None

for entry in ('main.tex', 'report.tex'):
    try:
        chains[entry] = walk(ROOT, entry)
        duplicates = {k: v for k, v in Counter(chains[entry]).items() if v != 1}
        if duplicates:
            errors.append({'duplicate_input': entry, 'paths': duplicates})
    except (OSError, ValueError) as exc:
        errors.append('Input traversal failed for ' + entry + ': ' + str(exc))

if baseline:
    prior_book = baseline['input_chains']['main.tex']
    prior_report = baseline['input_chains']['report.tex']
    expected_book = []
    if prior_book.count(OLD_SECTION13) != 1:
        errors.append('The recorded baseline does not contain exactly one inherited section 13')
    for name in prior_book:
        expected_book.extend(NEW_BOOK if name == OLD_SECTION13 else [name])
    if chains.get('main.tex') != expected_book:
        errors.append('Book input chain does not equal the old chain with exactly the new section-13 substitution')
    insertion = next((i for i, name in enumerate(prior_report) if name.startswith('reports/')), None)
    if insertion is None:
        errors.append('No prior report-module insertion boundary')
    else:
        expected_report = prior_report[:insertion] + NEW_REPORT + prior_report[insertion:]
        if chains.get('report.tex') != expected_report:
            errors.append('Report input chain must prepend the four new audits and retain every prior module in order')

book = chains.get('main.tex', [])
for number in range(69, 109):
    name = f'continuations/v18_batch{number:03d}.tex'
    if book.count(name) != 1:
        errors.append('Dot module missing or duplicated: ' + name)
if OLD_SECTION13 in book:
    errors.append('The inherited section 13 is still included alongside its replacement')

for name in NEW_BOOK + NEW_REPORT:
    try:
        if not regular(ROOT, name).read_text(encoding='utf-8').strip():
            errors.append('Empty new module: ' + name)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

try:
    old13 = regular(ROOT, OLD_SECTION13).read_bytes()
    archived13 = regular(ROOT, 'recollation/legacy_v20/v20_section13_inherited.tex').read_bytes()
    if old13 != archived13:
        errors.append('The old section-13 archive is not byte-identical to the preserved original')
except (OSError, ValueError) as exc:
    errors.append('Old section-13 preservation failed: ' + str(exc))
    old13 = b''

try:
    spec = importlib.util.spec_from_file_location('flatten', regular(ROOT, 'flatten_sources.py'))
    flat = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(flat)
    for entry, single in (('main.tex', 'single.tex'), ('report.tex', 'report_single.tex')):
        expanded = flat.expand(ROOT / entry)
        single_text = regular(ROOT, single).read_text(encoding='utf-8')
        if expanded != single_text:
            errors.append('Single source does not equal the current input expansion: ' + single)
        if re.search(r'\\(?:input|include)\{', single_text):
            errors.append('Single source still has an external input: ' + single)
except (OSError, ValueError, ImportError) as exc:
    errors.append('Single-file verification failed: ' + str(exc))

try:
    pre = regular(ROOT, 'preamble.tex').read_text(encoding='utf-8')
    if '\\documentclass[UTF8,a4paper]{ctexbook}' not in pre:
        errors.append('Unexpected document class')
    for command in (r'\\setCJKmainfont', r'\\setmainfont', r'\\geometry',
                    r'\\usepackage(?:\[[^]]*\])?\{geometry\}'):
        if re.search(command, pre):
            errors.append('Unexpected font or geometry override: ' + command)
except (OSError, ValueError) as exc:
    errors.append(str(exc))

notes = []
for name in NEW_BOOK:
    path = ROOT / name
    if path.is_file():
        notes.extend(re.findall(r'\\cmt\{([^}]+)\}', path.read_text(encoding='utf-8')))
duplicates = {k: v for k, v in Counter(notes).items() if v > 1}
if duplicates:
    errors.append({'duplicate_current_note_ids': duplicates})

result = {
    'edition': 21, 'pass': not errors, 'errors': errors,
    'source_records': len(set(sum(chains.values(), []))), 'input_chains': chains,
    'new_section13_modules': NEW_BOOK, 'new_report_modules': NEW_REPORT,
    'inherited_source_files_unchanged': sum(row['unchanged'] for row in preserved),
    'inherited_source_files_expected': len(preserved), 'preserved_source_records': preserved,
    'dot_modules_input_once': sum(book.count(f'continuations/v18_batch{n:03d}.tex') == 1
                                  for n in range(69, 109)),
    'baseline_commit': BASE_COMMIT,
    'baseline_comparison_mode': ('actual_previous_project_and_recorded_hashes'
                                 if reference_read else 'recorded_baseline_hashes_only'),
    'previous_project_actually_read_this_run': reference_read,
    'section13_preserved_original_bytes': len(old13),
    'current_section13_footnotes': len(notes),
    'scope': 'Inherited-file preservation, ordered inputs and standalone-source equality; not mathematical proof verification',
}
(ROOT / 'checks/current_structure_verification.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items()
                  if k not in ('input_chains', 'preserved_source_records')}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
