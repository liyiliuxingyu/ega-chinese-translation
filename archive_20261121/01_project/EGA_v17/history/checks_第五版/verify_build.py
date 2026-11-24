#!/usr/bin/env python3
"""Reproducible structural and PDF checks for EGA fifth edition."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
import re, json, hashlib, zipfile
import fitz
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'history/reference_v4.tex'
old=OLD.read_text(); new=(ROOT/'single.tex').read_text()
entrypat=r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}'
tagpat=r'\\tag\*?\{([^}]+)\}'
a,b=Counter(re.findall(entrypat,old)),Counter(re.findall(entrypat,new))
x,y=Counter(re.findall(tagpat,old)),Counter(re.findall(tagpat,new))
assert not a-b,dict(a-b)
assert not x-y,dict(x-y)
newfiles=sorted((ROOT/'continuations').glob('iv0_18_*.tex'))
s='\n'.join(p.read_text() for p in newfiles)
entries=re.findall(entrypat,s)
expected=[f'18.{i}.{j}' for i,n in enumerate([7,10,8,6,4],1) for j in range(1,n+1)]+['18.5.3.1']
assert Counter(entries)==Counter(expected),(entries,expected)
result={'numbered_entries':{'previous':sum(a.values()),'current':sum(b.values()),'new_section':len(entries),'missing_old':dict(a-b)},'formula_tags':{'previous':sum(x.values()),'current':sum(y.values()),'new_section':len(re.findall(tagpat,s)),'missing_old':dict(x-y)},'new_section_entry_list':entries,'new_section_formula_list':re.findall(tagpat,s),'new_tikzcd_environments':s.count(r'\begin{tikzcd}')}
# Compare preserved content files with hashes recorded from the original fourth-edition ZIP.
retained=[]
for rel,digest in json.loads((ROOT/'history/v4_content_hashes.json').read_text()).items():
    local=ROOT/rel
    assert local.exists(),rel
    assert hashlib.sha256(local.read_bytes()).hexdigest()==digest,rel
    retained.append(rel)
result['retained_tex_files_identical']=retained
result['pdf_pairs']={}
for label,p1,p2 in [('book',ROOT/'main.pdf',ROOT/'single_build/main_single.pdf'),('report',ROOT/'report.pdf',ROOT/'single_build/audit_single.pdf')]:
 d1,d2=fitz.open(p1),fitz.open(p2)
 assert len(d1)==len(d2)
 differences=[]; pixel_differences=[]; digests=[]
 for i in range(len(d1)):
  if d1[i].get_text()!=d2[i].get_text():differences.append(i+1)
  p,q=d1[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False),d2[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
  hp,hq=hashlib.sha256(p.samples).hexdigest(),hashlib.sha256(q.samples).hexdigest()
  if hp!=hq or p.width!=q.width or p.height!=q.height:pixel_differences.append(i+1)
  digests.append(hp)
 result['pdf_pairs'][label]={'pages':len(d1),'text_difference_pages':differences,'pixel_difference_pages_72dpi':pixel_differences,'page_pixel_sha256':digests,'pymupdf':fitz.VersionBind}
 assert not differences and not pixel_differences,(label,differences,pixel_differences)
logs={'book':'main.log','report':'report.log','standalone_book':'single_build/main_single.log','standalone_report':'single_build/audit_single.log'}
result['logs']={}
for key,rel in logs.items():
 text=(ROOT/rel).read_text(errors='replace')
 result['logs'][key]={name:len(re.findall(pat,text)) for name,pat in {'overfull':r'Overfull \\[hv]box','underfull':r'Underfull \\[hv]box','missing_glyph':r'Missing character:','undefined_control_sequence':r'Undefined control sequence','undefined_references':r'There were undefined references','errors':r'^!|LaTeX Error:|Package .* Error:','rerun_labels':r'Label\(s\) may have changed','font_size_substitution':r'Size substitutions with differences'}.items()}
for key,vals in result['logs'].items():
 assert not any(vals[n] for n in ['overfull','missing_glyph','undefined_control_sequence','undefined_references','errors','rerun_labels']),(key,vals)
(ROOT/'checks/build_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
short={k:v for k,v in result.items() if k not in ['new_section_entry_list','new_section_formula_list','pdf_pairs','retained_tex_files_identical']}
short['retained_files']=len(retained)
short['pdf_pairs']={k:{a:b for a,b in v.items() if a!='page_pixel_sha256'} for k,v in result['pdf_pairs'].items()}
print(json.dumps(short,ensure_ascii=False,indent=2))
