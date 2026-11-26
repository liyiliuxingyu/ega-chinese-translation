#!/usr/bin/env python3
"""Validate specifically listed edition-23 visual reviews against final PDFs.

This does not perform a human visual review or manufacture review records.
Create checks/visual_review_plan.json only after selecting actual pages:
{
  "schema_version": 1, "edition": 23,
  "required_pages": {"main": [1, 2], "report": [1, 2]},
  "review_records": ["checks/v23_main_visual.json", "checks/v23_report_visual.json"]
}
Each review record has schema_version=1, edition=23, a nonempty reviewer,
review_method="actual_image_view", document="main" or "report",
pdf={"path":"main.pdf","sha256":"..."}, rendering={"renderer":"PyMuPDF","scale":1.65},
and pages=[{"physical_page":1,"image":"checks/...png","image_sha256":"...",
"verdict":"pass","notes":"Actual visual observations"}].
All images must be full-page RGB PyMuPDF renders at the recorded scale, alpha=False.
The checker re-renders those pages and compares actual image pixels. If layout
changes, render and view affected pages again; an old PDF binding fails.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import re

import fitz

ROOT = Path(__file__).resolve().parents[1]
EDITION = 23
SHA = re.compile(r'^[0-9a-f]{64}$')
errors, records = [], []
pdfs, documents, final_hashes = {}, {}, {}
plan = None


def regular(name):
    if not isinstance(name, str):
        raise ValueError('File path must be a string')
    rel = PurePosixPath(name)
    if (not name or rel.is_absolute() or '..' in rel.parts or '\\' in name
            or rel.as_posix() != name):
        raise ValueError('Unsafe project path: ' + name)
    path = ROOT / name
    if (not path.is_file() or path.is_symlink()
            or not path.resolve().is_relative_to(ROOT)
            or any(p.is_symlink() for p in path.parents if p != ROOT)):
        raise ValueError('Missing or unsafe regular project file: ' + name)
    return path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads(regular(name).read_text(encoding='utf-8'))


def is_page_number(value):
    return type(value) is int and value > 0


try:
    plan = read('checks/visual_review_plan.json')
    if plan.get('schema_version') != 1 or plan.get('edition') != EDITION:
        raise ValueError('Visual review plan must target edition 23, schema 1')
    required = plan['required_pages']
    if set(required) != {'main', 'report'}:
        raise ValueError('Required-page plan must specify main and report')
    for kind, pages in required.items():
        if (not isinstance(pages, list) or not pages
                or any(not is_page_number(p) for p in pages)
                or len(pages) != len(set(pages))):
            raise ValueError('Required-page list must be nonempty, positive and unique: ' + kind)
    review_names = plan['review_records']
    if (not isinstance(review_names, list) or not review_names
            or any(not isinstance(n, str) for n in review_names)
            or len(review_names) != len(set(review_names))):
        raise ValueError('Review record list must be nonempty and unique')
    for name in review_names:
        if not name.startswith('checks/') or not name.endswith('.json'):
            raise ValueError('Expected a review JSON in checks/: ' + name)
except (OSError, ValueError, KeyError, TypeError) as exc:
    errors.append('Invalid or missing current visual plan: ' + str(exc))
    plan = None

for kind in ('main', 'report'):
    try:
        pdfs[kind] = regular(kind + '.pdf')
        final_hashes[kind] = sha(pdfs[kind])
        documents[kind] = fitz.open(pdfs[kind])
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append('Final PDF unavailable: ' + kind + ': ' + str(exc))

if plan:
    for review_name in plan['review_records']:
        try:
            review = read(review_name)
            if review.get('schema_version') != 1 or review.get('edition') != EDITION:
                raise ValueError('Review belongs to another edition/schema')
            if (review.get('review_method') != 'actual_image_view'
                    or not isinstance(review.get('reviewer'), str)
                    or not review['reviewer'].strip()):
                raise ValueError('Missing actual-image-view declaration or reviewer')
            kind = review['document']
            if kind not in ('main', 'report') or kind not in documents:
                raise ValueError('Missing or invalid reviewed final document')
            binding = review['pdf']
            if binding['path'] != kind + '.pdf' or binding['sha256'] != final_hashes[kind]:
                raise ValueError('Review is not bound to the final PDF bytes')
            rendering = review['rendering']
            if rendering['renderer'] != 'PyMuPDF':
                raise ValueError('Expected reproducible full-page PyMuPDF renders')
            scale = rendering['scale']
            if (type(scale) not in (int, float) or not math.isfinite(scale)
                    or not 0.5 <= scale <= 6):
                raise ValueError('Invalid render scale')
            pages = review['pages']
            if not isinstance(pages, list) or not pages:
                raise ValueError('Empty review page list')
            seen_here = set()
            for page_record in pages:
                page_number = page_record['physical_page']
                if (not is_page_number(page_number) or page_number > len(documents[kind])
                        or page_number in seen_here):
                    raise ValueError('Duplicate or out-of-range physical page')
                seen_here.add(page_number)
                if page_record.get('verdict') != 'pass':
                    raise ValueError('Review contains an unresolved page verdict')
                if (not isinstance(page_record.get('notes'), str)
                        or not page_record['notes'].strip()):
                    raise ValueError('Actual page observations are missing')
                image_name = page_record['image']
                image_path = regular(image_name)
                image_hash = page_record['image_sha256']
                if not isinstance(image_hash, str) or not SHA.fullmatch(image_hash):
                    raise ValueError('Invalid recorded image SHA-256')
                if sha(image_path) != image_hash:
                    raise ValueError('Viewed image bytes have changed: ' + image_name)
                expected = documents[kind][page_number - 1].get_pixmap(
                    matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
                observed = fitz.Pixmap(str(image_path))
                if (observed.width != expected.width or observed.height != expected.height
                        or observed.n != 3 or observed.alpha
                        or observed.samples != expected.samples):
                    raise ValueError('Viewed image is not this final PDF page render: '
                                     + kind + ' page ' + str(page_number))
                records.append({
                    'document': kind, 'physical_page': page_number,
                    'review_record': review_name, 'reviewer': review['reviewer'],
                    'image': image_name, 'image_sha256': image_hash,
                    'scale': scale, 'pixels_match_final_pdf_page': True,
                })
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            errors.append('Invalid current visual review ' + review_name + ': ' + str(exc))

pages = {kind: sorted({r['physical_page'] for r in records if r['document'] == kind})
         for kind in ('main', 'report')}
if plan:
    for kind in ('main', 'report'):
        missing = set(plan['required_pages'][kind]) - set(pages[kind])
        if missing:
            errors.append({'required_visual_pages_not_passed': kind, 'pages': sorted(missing)})
        if kind in documents and any(p > len(documents[kind]) for p in plan['required_pages'][kind]):
            errors.append('Required-page plan exceeds the final PDF: ' + kind)

for document in documents.values():
    document.close()

result = {
    'edition': EDITION, 'pass': not errors, 'errors': errors,
    'final_pdf_sha256': final_hashes,
    'review_plan': 'checks/visual_review_plan.json',
    'actual_reviewed_distinct_pages': pages,
    'actual_reviewed_distinct_page_count': sum(map(len, pages.values())),
    'records': records,
    'whole_book_human_page_by_page_review': False,
    'scope': 'Only explicitly recorded actual image views, with exact final-PDF binding '
             'and re-rendered pixel equality. This tool does not itself visually review pages '
             'or infer reviews from old records. All-page modular/single parity is separate.',
}
(ROOT / 'checks/visual_verification_summary.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'records'},
                 ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
