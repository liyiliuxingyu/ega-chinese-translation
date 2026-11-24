#!/usr/bin/env python3
"""Compare compiled variants page-by-page with MuPDF at 72 dpi.

Use: python checks/verify_pdfs.py --independent /path/to/independent
Text and pixel equality are layout checks, not mathematical verification.
"""
from pathlib import Path
import argparse,hashlib,json,fitz
P=argparse.ArgumentParser();P.add_argument('--independent',type=Path,required=True);a=P.parse_args()
ROOT=Path(__file__).resolve().parents[1]
res={}
for stem,other in [('main','book_single'),('report','audit_single')]:
 p=ROOT/f'{stem}.pdf';q=a.independent/f'{other}.pdf'
 x=fitz.open(p);y=fitz.open(q)
 assert len(x)==len(y),(stem,len(x),len(y))
 texts=[];pixels=[];perpage=[]
 for i in range(len(x)):
  tx=x[i].get_text();ty=y[i].get_text()
  if tx!=ty:texts.append(i+1)
  px=x[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  py=y[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  hx=hashlib.sha256(px.samples).hexdigest();hy=hashlib.sha256(py.samples).hexdigest()
  if (px.width,px.height,hx)!=(py.width,py.height,hy):pixels.append(i+1)
  perpage.append({'pdf_page':i+1,'text_sha256':hashlib.sha256(tx.encode()).hexdigest(),'pixel_sha256':hx,'width':px.width,'height':px.height})
 res[stem]={'page_count':len(x),'text_mismatches':texts,'pixel_mismatches_72dpi':pixels,'renderer':'MuPDF '+fitz.VersionBind,
 'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 (ROOT/f'checks/{stem}_page_hashes.json').write_text(json.dumps(perpage,indent=2))
 assert not texts and not pixels,res[stem]
(ROOT/'checks/pdf_comparison.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))
