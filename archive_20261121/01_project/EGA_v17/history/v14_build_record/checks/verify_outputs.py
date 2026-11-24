from pathlib import Path
import json,re,hashlib,time
import fitz
ROOT=Path(__file__).resolve().parents[1]
checks=ROOT/'checks'
result={'renderer':'PyMuPDF '+fitz.VersionBind,'dpi':72,'pairs':{},'logs':{}}
for title,a,b in [('book','main.pdf','single_build/book_single.pdf'),('report','report.pdf','single_build/audit_single.pdf')]:
    d1,d2=fitz.open(ROOT/a),fitz.open(ROOT/b)
    item={'pages_main':len(d1),'pages_single':len(d2),'text_mismatch_pages':[],'pixel_mismatch_pages':[],'page_size_mismatch_pages':[]}
    if len(d1)==len(d2):
        for i in range(len(d1)):
            p1,p2=d1[i],d2[i]
            if p1.get_text()!=p2.get_text(): item['text_mismatch_pages'].append(i+1)
            if p1.rect!=p2.rect:item['page_size_mismatch_pages'].append(i+1)
            x1,x2=p1.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False),p2.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            if x1.width!=x2.width or x1.height!=x2.height or hashlib.sha256(x1.samples).digest()!=hashlib.sha256(x2.samples).digest():item['pixel_mismatch_pages'].append(i+1)
            if (i+1)%100==0:print(title,i+1,flush=True)
    item['all_text_equal']=not item['text_mismatch_pages'] and len(d1)==len(d2)
    item['all_pixels_equal']=not item['pixel_mismatch_pages'] and len(d1)==len(d2)
    result['pairs'][title]=item
    for name in [a,b]:
        log=(ROOT/name).with_suffix('.log').read_text(errors='replace')
        pats={'latex_errors':r'^!|LaTeX Error|Undefined control sequence','missing_chars':r'Missing character:','undefined_references':r'(?:Reference|Citation) .+ undefined|There were undefined references','overfull_boxes':r'Overfull \\[hv]box','underfull_boxes':r'Underfull \\[hv]box','font_warnings':r'LaTeX Font Warning:','hyperref_warnings':r'Package hyperref Warning:'}
        result['logs'][name]={k:len(re.findall(pat,log,re.M)) for k,pat in pats.items()}
        warnings=[]
        lines=log.splitlines()
        for j,line in enumerate(lines):
            if 'Warning:' in line or 'Underfull' in line or 'Overfull' in line or 'Missing character' in line or line.startswith('!'):
                warnings.append('\n'.join(lines[j:j+5]))
        (checks/(Path(name).stem+'_warnings.txt')).write_text('\n\n'.join(warnings))
    print(title,'complete',item,flush=True)
(checks/'output_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
