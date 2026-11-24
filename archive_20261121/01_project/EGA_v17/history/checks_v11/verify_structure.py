#!/usr/bin/env python3
"""Check source coverage against the exact tenth-edition baseline.

This is a structural/file-integrity check, not a mathematical proof checker.
"""
from pathlib import Path
from collections import Counter
import hashlib, json, re
P=Path(__file__).resolve().parents[1]
old=json.loads((P/'checks/baseline_body_v10_sha256.json').read_text())
changed=[]; missing=[]; unchanged=[]
for name, expected in old.items():
    f=P/name
    if not f.is_file(): missing.append(name)
    elif hashlib.sha256(f.read_bytes()).hexdigest()!=expected:changed.append(name)
    else:unchanged.append(name)
text=(P/'single.tex').read_text()
base=json.loads((P/'checks/baseline_structure_v10.json').read_text())
entries=re.findall(r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}',text)
tags=re.findall(r'\\tag\{([^}]+)\}',text)
new_files=sorted((P/'continuations').glob('iv0_21_*.tex'))
new_text='\n'.join(f.read_text() for f in new_files)
new_entries=re.findall(r'\\(?:egap|egas)\{([^}]+)\}',new_text)
new_tags=re.findall(r'\\tag\{([^}]+)\}',new_text)
expected=[f'21.1.{n}' for n in range(1,11)]+['21.1.6.1']+[f'21.2.{n}' for n in range(1,9)]+[f'21.3.{n}' for n in range(1,7)]+[f'21.4.{n}' for n in range(0,9)]
result={
 'baseline_files':len(old), 'unchanged_files':unchanged,'changed_files':changed,'missing_files':missing,
 'intentional_nonmathematical_change':'text/remaining.tex',
 'entry_regex':r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}',
 'baseline_entry_macro_count':len(base['entries']), 'current_entry_macro_count':len(entries),
 'baseline_tag_macro_count':len(base['tags']), 'current_tag_macro_count':len(tags),
 'lost_entry_macro_occurrences':dict(Counter(base['entries'])-Counter(entries)),
 'lost_tag_macro_occurrences':dict(Counter(base['tags'])-Counter(tags)),
 'new_entry_count':len(new_entries),'new_entries_in_source_order':new_entries,
 'new_tag_count':len(new_tags),'new_tags':new_tags,
 'new_tikzcd_count':new_text.count(r'\begin{tikzcd}'),
 'missing_new_entries':list((Counter(expected)-Counter(new_entries)).elements()),
 'unexpected_new_entries':list((Counter(new_entries)-Counter(expected)).elements()),
 'next_source_position':'0-IV 21.5 introductory note and (21.5.1); EGAIV.1 PDF page 163, printed page 164',
 'scope_note':'Counts refer only to these TeX macros; they are not a count of every equation or every mathematical assertion in the book.'}
assert not missing and changed==['text/remaining.tex'],result
assert not result['lost_entry_macro_occurrences'] and not result['lost_tag_macro_occurrences'],result
assert not result['missing_new_entries'] and not result['unexpected_new_entries'],result
assert len(new_entries)==34 and len(new_tags)==23 and result['new_tikzcd_count']==4
(P/'checks/structure_v11.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['unchanged_files','new_entries_in_source_order','new_tags']},ensure_ascii=False,indent=2))
