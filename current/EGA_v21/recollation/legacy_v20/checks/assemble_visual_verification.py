#!/usr/bin/env python3
"""Bind actual, specifically listed human page reviews to the final PDFs.

This validates review artifacts and pixel-equality carry-forward evidence. It does
not itself inspect a page visually or extend the reviewers' stated coverage.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):
    return json.loads((ROOT / 'checks' / name).read_text())

errors, records = [], []
final = {kind: sha(ROOT / (name + '.pdf'))
         for kind, name in [('main', 'main'), ('report', 'report')]}
rebinding = read('main_visual_rebinding.json')
rebound = {row['page']: row for row in rebinding['pages']}
if rebinding['new_pdf_sha256'] != final['main']:
    errors.append('Main pixel rebinding is stale')

def image_check(name, digest):
    path = ROOT / name
    if not path.is_file() or sha(path) != digest:
        errors.append('Review image missing or changed: ' + name)

root = read('v20_root_visual.json')
for kind in ['main', 'report']:
    if root[kind + '_pdf']['sha256'] != final[kind]:
        errors.append('Root review PDF binding is stale: ' + kind)
    for row in root[kind + '_pages']:
        page = row['physical_page']
        if kind == 'main':
            image_check(row['actual_viewed_image'], row['actual_viewed_image_sha256'])
            image_check(row['final_image'], row['final_image_sha256'])
            if not rebound[page]['pixels_unchanged']:
                errors.append('Previously viewed root main page changed: ' + str(page))
        else:
            image_check(row['image'], row['sha256'])
        if row['result'] != 'pass':
            errors.append('Root review has unresolved issue')
        records.append({'document': kind, 'physical_page': page,
                        'record': 'checks/v20_root_visual.json'})

for name in ['v20_opening_report_visual.json', 'v20_extensions_report_visual.json',
             'v20_degeneracy_report_visual.json']:
    data = read(name)
    pdf = data.get('report_pdf', data.get('pdf'))
    if pdf['sha256'] != final['report']:
        errors.append('Report review PDF binding is stale: ' + name)
    for row in data['pages']:
        image_path = row.get('png_path', row.get('png', row.get('image')))
        image_digest = row.get('png_sha256', row.get('sha256'))
        image_check(image_path, image_digest)
        verdict = row.get('result', row.get('verdict'))
        if not verdict.startswith('pass'):
            errors.append('Report review has unresolved issue: ' + name)
        records.append({'document': 'report', 'physical_page': row['physical_page'],
                        'record': 'checks/' + name})

data = read('v20_degeneracy_visual.json')
if data['main_pdf']['sha256'] != rebinding['old_pdf_sha256']:
    errors.append('Unexpected original degeneracy review PDF')
for row in data['pages']:
    page = row['physical_page']
    image_check(row['image'], row['sha256'])
    if not rebound[page]['pixels_unchanged']:
        errors.append('Previously viewed degeneracy page changed: ' + str(page))
    records.append({'document': 'main', 'physical_page': page,
                    'record': 'checks/v20_degeneracy_visual.json',
                    'final_binding': 'checks/main_visual_rebinding.json'})

data = read('v20_opening_extensions_visual.json')
if data['main_pdf']['sha256'] != final['main']:
    errors.append('Opening/extensions main review has not been updated to final PDF')
if data['overall_verdict'] != 'pass':
    errors.append('Opening/extensions main review has unresolved observations')
for row in data['pages']:
    image_path = row.get('image_path', row.get('png_path'))
    image_digest = row.get('image_sha256', row.get('png_sha256'))
    image_check(image_path, image_digest)
    if row.get('verdict') != 'pass':
        errors.append('Opening/extensions page failed review')
    records.append({'document': 'main', 'physical_page': row['physical_page'],
                    'record': 'checks/v20_opening_extensions_visual.json'})

pages = {kind: sorted({row['physical_page'] for row in records if row['document'] == kind})
         for kind in ['main', 'report']}
result = {
    'pass': not errors, 'errors': errors, 'final_pdf_sha256': final,
    'actual_reviewed_distinct_pages': pages,
    'actual_reviewed_distinct_page_count': sum(map(len, pages.values())),
    'records': records,
    'last_layout_change': 'Two intact extension footnotes attached to their introducing clauses; '
        'the six affected/nearby main pages were rendered and actually reviewed again. '
        'Ten previously viewed root/degeneracy pages were rebound through exact 1.65-scale '
        'pixel identity; the final cover was directly viewed.',
    'whole_book_human_page_by_page_review': False,
    'scope': 'Listed human sample reviews and final artifact bindings only. '
             'Automatic all-page module/single equality is separately recorded in current_pdf_parity.json.',
}
(ROOT / 'checks/visual_verification_summary.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['pass', 'errors', 'actual_reviewed_distinct_pages',
                                       'actual_reviewed_distinct_page_count']}, indent=2))
raise SystemExit(bool(errors))
