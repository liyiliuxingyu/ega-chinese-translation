from pathlib import Path
import fitz,hashlib,json,re,zipfile,collections
root=Path(__file__).resolve().parents[1]
result={'version':'第七版','renderer':'PyMuPDF','render_dpi':72,'comparisons':{},'logs':{}}
for name,a,b in [('book',root/'main.pdf',root/'single_build/book_single.pdf'),('audit',root/'report.pdf',root/'single_build/audit_single.pdf')]:
 d1,d2=fitz.open(a),fitz.open(b)
 rec={'pages_multi':len(d1),'pages_single':len(d2),'text_differences':[],'pixel_differences':[],'page_hashes':[]}
 for i in range(min(len(d1),len(d2))):
  ts=[hashlib.sha256(d[i].get_text().encode()).hexdigest() for d in (d1,d2)]
  px=[hashlib.sha256(d[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).samples).hexdigest() for d in (d1,d2)]
  if ts[0]!=ts[1]:rec['text_differences'].append(i+1)
  if px[0]!=px[1]:rec['pixel_differences'].append(i+1)
  rec['page_hashes'].append({'page':i+1,'text':ts[0],'pixels':px[0]})
 (root/f'checks/{name}_page_comparison.json').write_text(json.dumps(rec,indent=2))
 result['comparisons'][name]={k:v for k,v in rec.items() if k!='page_hashes'}
for f in [root/'main.log',root/'report.log',root/'single_build/book_single.log',root/'single_build/audit_single.log']:
 t=f.read_text(errors='replace')
 result['logs'][str(f.relative_to(root))]={
 'latex_error':len(re.findall(r'^! ',t,re.M)),
 'undefined_control_sequence':t.count('Undefined control sequence'),
 'missing_characters':t.count('Missing character:'),
 'undefined_references':t.count('There were undefined references'),
 'overfull_boxes':t.count('Overfull \\'),
 'underfull_boxes':t.count('Underfull \\'),
 'font_warnings':t.count('LaTeX Font Warning:'),
 'rerun_requested':('Rerun to get' in t or 'rerunfilecheck Warning' in t),
 }
result['coverage']=json.loads((root/'checks/coverage.json').read_text())
result['visually_reviewed']={'book_pdf_pages':[1,3,4,5]+list(range(270,296)),'audit_pdf_pages':list(range(13,24)),'method':'Contact sheets and selected full-page enlargements; not independent mathematical peer review.'}
(root/'checks/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
