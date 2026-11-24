#!/usr/bin/env python3
"""Compare multi-file and independently compiled single-file PDFs, page by page."""
from pathlib import Path
import fitz,hashlib,json,re,time
root=Path(__file__).resolve().parents[1]
result={'version':'第八版','renderer':'PyMuPDF','render_dpi':72,'comparisons':{},'logs':{},'started':time.strftime('%Y-%m-%dT%H:%M:%S')}
for name,a,b in [('book',root/'main.pdf',root/'single_build/book_single.pdf'),('audit',root/'report.pdf',root/'single_build/audit_single.pdf')]:
 d1,d2=fitz.open(a),fitz.open(b)
 rec={'pages_multi':len(d1),'pages_single':len(d2),'text_differences':[],'pixel_differences':[],'page_hashes':[]}
 for i in range(min(len(d1),len(d2))):
  ts=[hashlib.sha256(d[i].get_text().encode()).hexdigest() for d in (d1,d2)]
  px=[hashlib.sha256(d[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).samples).hexdigest() for d in (d1,d2)]
  if ts[0]!=ts[1]:rec['text_differences'].append(i+1)
  if px[0]!=px[1]:rec['pixel_differences'].append(i+1)
  rec['page_hashes'].append({'page':i+1,'text':ts[0],'pixels':px[0]})
  if i%50==0:(root/'checks/comparison_progress.json').write_text(json.dumps({'document':name,'compared_pages':i+1,'total_pages':len(d1)}))
 (root/f'checks/{name}_page_comparison.json').write_text(json.dumps(rec,indent=2))
 result['comparisons'][name]={k:v for k,v in rec.items() if k!='page_hashes'}
for f in [root/'main.log',root/'report.log',root/'single_build/book_single.log',root/'single_build/audit_single.log']:
 t=f.read_text(errors='replace')
 result['logs'][str(f.relative_to(root))]={
 'latex_errors':len(re.findall(r'^! ',t,re.M)),
 'undefined_control_sequences':t.count('Undefined control sequence'),
 'missing_characters':t.count('Missing character:'),
 'undefined_references':t.count('There were undefined references'),
 'overfull_boxes':t.count('Overfull \\'),
 'underfull_boxes':t.count('Underfull \\'),
 'font_warnings':t.count('LaTeX Font Warning:'),
 'rerun_requested':('Rerun to get' in t or 'rerunfilecheck Warning' in t),
 }
result['coverage']=json.loads((root/'checks/coverage.json').read_text())
result['finished']=time.strftime('%Y-%m-%dT%H:%M:%S')
(root/'checks/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
assert all(v['pages_multi']==v['pages_single'] and not v['text_differences'] and not v['pixel_differences'] for v in result['comparisons'].values())
assert not any(v[k] for v in result['logs'].values() for k in ['latex_errors','undefined_control_sequences','missing_characters','undefined_references','overfull_boxes','rerun_requested'])
