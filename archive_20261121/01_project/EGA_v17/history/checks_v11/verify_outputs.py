#!/usr/bin/env python3
"""Compare project and standalone builds and scan final logs.
Pixel comparison uses one renderer (PyMuPDF) at 72 dpi. It is not a visual/math audit.
"""
from pathlib import Path
import fitz,hashlib,json,re,time
P=Path(__file__).resolve().parents[1]
start=time.time();pairs=[]
for main,single in [('main.pdf','single_build/book_single.pdf'),('report.pdf','single_build/audit_single.pdf')]:
    a=fitz.open(P/main);b=fitz.open(P/single)
    assert len(a)==len(b),(main,len(a),len(b))
    text_bad=[];pixel_bad=[];sizes=[]
    hashes=[]
    for n,(x,y) in enumerate(zip(a,b)):
        if x.get_text()!=y.get_text():text_bad.append(n+1)
        px=x.get_pixmap(dpi=72,alpha=False);py=y.get_pixmap(dpi=72,alpha=False)
        hx=hashlib.sha256(px.samples).hexdigest();hy=hashlib.sha256(py.samples).hexdigest()
        if px.width!=py.width or px.height!=py.height or hx!=hy:pixel_bad.append(n+1)
        hashes.append(hx)
        if abs(x.rect.width-595.276)>1 or abs(x.rect.height-841.89)>1:sizes.append(n+1)
    item={'project_pdf':main,'standalone_pdf':single,'pages':len(a),'text_mismatch_pages':text_bad,'pixel_mismatch_pages':pixel_bad,'non_a4_pages':sizes,'renderer':'PyMuPDF '+fitz.VersionBind,'comparison_dpi':72,'pixel_sha256_by_page':hashes}
    pairs.append(item)
    assert not(text_bad or pixel_bad or sizes),item
logs={}
for name in ['main.log','report.log','single_build/book_single.log','single_build/audit_single.log']:
    t=(P/name).read_text(errors='replace')
    checks={'tex_errors':r'^!','undefined_control':r'Undefined control sequence','missing_characters':r'Missing character:','undefined_references':r'There were undefined references|Reference .+ undefined','overfull_boxes':r'Overfull \\[hv]box','rerun_warnings':r'Label\(s\) may have changed|Rerun to get|Rerun to get outlines right','underfull_boxes':r'Underfull \\[hv]box','font_warnings':r'LaTeX Font Warning:'}
    logs[name]={k:len(re.findall(v,t,re.M)) for k,v in checks.items()}
    assert not any(logs[name][k] for k in ('tex_errors','undefined_control','missing_characters','undefined_references','overfull_boxes','rerun_warnings')),logs[name]
result={'pairs':pairs,'logs':logs,'duration_seconds':round(time.time()-start,2),'limitation':'Equality of text and 72 dpi raster output is a build-consistency check only; it does not establish translation fidelity or mathematical correctness.'}
(P/'checks/output_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'pairs':[{k:v for k,v in x.items() if k!='pixel_sha256_by_page'} for x in pairs],'logs':logs,'seconds':result['duration_seconds']},ensure_ascii=False,indent=2))
