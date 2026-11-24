"""Verify v15 preservation, v16 coverage, and reproducible source flattening."""
from pathlib import Path
from collections import Counter
import hashlib, json, re, importlib.util
ROOT=Path(__file__).resolve().parents[1]; CHECKS=ROOT/'checks'
spec=importlib.util.spec_from_file_location('flatten',ROOT/'flatten_sources.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
book=mod.expand(ROOT/'main.tex');report=mod.expand(ROOT/'report.tex')
assert book==(ROOT/'single.tex').read_text()
assert report==(ROOT/'report_single.tex').read_text()
prev=json.loads((CHECKS/'baseline_v15_counters.json').read_text())
patterns={'entries':r'\\(?:egap|egas|egapar|egastatement)\{([^}]+)\}','tags':r'\\tag\{([^}]+)\}'}
result={}
for key,pat in patterns.items():
 new=re.findall(pat,book);a,b=Counter(prev[key]),Counter(new)
 result[key]={'old_total':len(prev[key]),'new_total':len(new),'missing':dict(a-b),'added':dict(b-a)}
 assert not result[key]['missing'],result[key]
for key,name in [('math_files','baseline_v15_math_sha256.json'),('historical_report_files','baseline_v15_reports_sha256.json')]:
 old=json.loads((CHECKS/name).read_text());changed=[n for n,h in old.items() if not (ROOT/n).exists() or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
 result[key]={'baseline_count':len(old),'changed':changed};assert not changed,changed
text='\n'.join((ROOT/'continuations'/n).read_text() for n in ['iv0_23_1.tex','iv0_23_2.tex'])
expected=[f'23.1.{i}' for i in range(1,8)]+['23.1.3.1']+[f'23.2.{i}' for i in range(1,11)]+['23.2.7.1']
entries=re.findall(patterns['entries'],text);assert Counter(entries)==Counter(expected)
result['new_content']={'entries':entries,'tags':re.findall(patterns['tags'],text),'footnotes':re.findall(r'\\cmt\{([^}]+)\}',text),'original_footnotes':text.count(r'\orig{'),'tikzcd_diagrams':text.count(r'\begin{tikzcd}')}
assert len(result['new_content']['tags'])==3
assert len(result['new_content']['footnotes'])==12
assert '待续' in text
(CHECKS/'structure_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
