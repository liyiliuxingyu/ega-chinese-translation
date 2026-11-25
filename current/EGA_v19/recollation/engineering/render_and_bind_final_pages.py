#!/usr/bin/env python3
"""Render the specified edition-19 sample; pixel equality does not imply human review."""
from pathlib import Path
import argparse
import hashlib
import json
import fitz
from PIL import Image, ImageChops


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', type=Path, required=True)
parser.add_argument('--previous-render', type=Path, required=True)
args = parser.parse_args()
root = args.project.resolve()
previous = args.previous_render.resolve()
out = root / 'checks/v19_visual_final'
out.mkdir(parents=True, exist_ok=True)
rows = []
for name, pages in [('main', [1, 3, 5, 7] + list(range(1031, 1055))),
                    ('report', [1, 3, 5] + list(range(19, 50)))]:
    path = root / (name + '.pdf')
    before = sha(path)
    with fitz.open(path) as doc:
        for page in pages:
            dest = out / f'{name}_{page:04d}.png'
            pix = doc[page-1].get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
            pix.save(dest)
            old = previous / dest.name
            a = Image.open(dest).convert('RGB')
            b = Image.open(old).convert('RGB')
            box = ImageChops.difference(a, b).getbbox() if a.size == b.size else 'size mismatch'
            rows.append({'pdf': path.name, 'pdf_sha256': before, 'physical_page': page,
                         'image': dest.name, 'image_sha256': sha(dest),
                         'rgb_sha256': hashlib.sha256(a.tobytes()).hexdigest(),
                         'previous_image_sha256': sha(old),
                         'same_png_bytes_as_previous_review': sha(old) == sha(dest),
                         'same_pixels_as_previous_review': box is None,
                         'changed_pixel_bounds': box})
    if before != sha(path):
        raise RuntimeError('PDF changed while rendering: ' + path.name)
result = {'dpi': 115.2, 'renderer': 'PyMuPDF '+fitz.VersionBind,
          'scope': 'Final PDF raster binding only; actual human inspection is recorded separately.',
          'pages': rows}
(out / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'rendered': len(rows), 'changed_pages': [r for r in rows if not r['same_pixels_as_previous_review']]},
                 ensure_ascii=False, indent=2))
