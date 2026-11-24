"""Compare modular and standalone PDFs: every page's text, size, 72dpi raster."""
from pathlib import Path
import fitz,json,time,gc,hashlib
R=Path(__file__).resolve().parents[1];start=time.time()
res={'renderer':f'PyMuPDF {fitz.VersionBind}','dpi':72,'outputs':{}}
for key,a,b in [('book',R/'main.pdf',R/'single_build/book_single.pdf'),('report',R/'report.pdf',R/'single_build/audit_single.pdf')]:
 d,e=fitz.open(a),fitz.open(b);assert len(d)==len(e),(key,len(d),len(e))
 dif={'text':[],'size':[],'pixels':[]};acc=hashlib.sha256()
 for i in range(len(d)):
  p,q=d[i],e[i]
  if p.get_text()!=q.get_text():dif['text'].append(i+1)
  if p.rect!=q.rect:dif['size'].append(i+1)
  pm=p.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);qm=q.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  if pm.samples!=qm.samples:dif['pixels'].append(i+1)
  acc.update(pm.samples)
  if i%100==0: print(key,i+1,'/',len(d),flush=True)
  del pm,qm
 res['outputs'][key]={'pages':len(d),'mismatches':dif,'page_raster_digest':acc.hexdigest(),'metadata':d.metadata}
 assert not any(dif.values()),dif
 d.close();e.close();gc.collect()
res['seconds']=time.time()-start
(R/'checks/output_verification.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2),flush=True)
