#!/usr/bin/env python3
"""Compare split-project and standalone builds using PyMuPDF at 72 dpi.
This is build reproducibility, not an independent proof/content validation.
"""
from pathlib import Path
import hashlib,json
import fitz
ROOT=Path(__file__).resolve().parents[1]
results=[]
for a,b in [('main.pdf','single_build/book_single.pdf'),('report.pdf','single_build/audit_single.pdf')]:
 x,y=fitz.open(ROOT/a),fitz.open(ROOT/b)
 assert len(x)==len(y),(a,len(x),len(y))
 text_diff=[];pixel_diff=[]
 for i,(p,q) in enumerate(zip(x,y),1):
  if p.get_text()!=q.get_text():text_diff.append(i)
  px=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  py=q.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  if (px.width,px.height)!=(py.width,py.height) or hashlib.sha256(px.samples).digest()!=hashlib.sha256(py.samples).digest():pixel_diff.append(i)
 result={'split_pdf':a,'standalone_pdf':b,'pages':len(x),'dpi':72,
         'text_differences':text_diff,'pixel_differences':pixel_diff,
         'status':'passed' if not(text_diff or pixel_diff) else 'failed'}
 results.append(result)
 print(json.dumps(result,ensure_ascii=False),flush=True)
(ROOT/'checks/build_comparison.json').write_text(json.dumps({'renderer':f'PyMuPDF {fitz.VersionBind}','results':results},ensure_ascii=False,indent=2))
assert all(r['status']=='passed' for r in results)
