#!/usr/bin/env python3
"""Check coverage, preserve old numbered entries, and report actual LaTeX diagnostics."""
from pathlib import Path
from collections import Counter
import re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASELINE=json.loads((ROOT/'checks/baseline_v5_counts.json').read_text())
new=(ROOT/'single.tex').read_text()
# Counts retain repeated numbers from different chapters; compare multiplicity.
entry=re.compile(r'\\(?:egapar|egastatement|egap|egas)\{([0-9]+(?:\.[0-9]+)*)\}')
tag=re.compile(r'\\tag\*?\{([^}]+)\}')
a,b=Counter(BASELINE['entries']),Counter(entry.findall(new))
ta,tb=Counter(BASELINE['formula_tags']),Counter(tag.findall(new))
addition='\n'.join((ROOT/x).read_text() for x in ['continuations/iv0_19_01.tex','continuations/iv0_19_23.tex','continuations/iv0_19_4.tex'])
new_ids=entry.findall(addition)
expected=[f'19.0.{i}' for i in range(1,4)]+[f'19.1.{i}' for i in range(1,16)]+[f'19.2.{i}' for i in range(1,6)]+[f'19.3.{i}' for i in range(1,13)]+['19.3.4.1','19.3.8.1','19.3.10.1','19.3.10.2']+[f'19.4.{i}' for i in range(1,8)]
assert Counter(new_ids)==Counter(expected)
assert not a-b,'Old entry lost'
assert not ta-tb,'Old formula tag lost'
assert b-a==Counter(new_ids),'Unexpected change in old entry multiplicity'
assert tb-ta==Counter(['19.4.4.1'])
# All notes used in the body must exist in the new report.
note_ids=sorted(set(re.findall(r'\\cmt\{(F6-[A-Z]\d+)\}',addition)))
report=(ROOT/'reports/sixth_audit.tex').read_text()
assert all('\\audit{'+x+'}' in report for x in note_ids)
base=json.loads((ROOT/'history/v5_content_hashes.json').read_text())
body_changes=[]
body_ok=[]
for rel,sha in base.items():
 if rel.startswith(('text/','continuations/')) and rel!='text/remaining.tex':
  got=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
  (body_ok if sha==got else body_changes).append(rel)
assert not body_changes,body_changes
logs={}
for stem in ['main','report']:
 s=(ROOT/(stem+'.log')).read_text(errors='replace')
 logs[stem]={
  'latex_error':s.count('LaTeX Error'),'undefined_control_sequence':s.count('Undefined control sequence'),
  'missing_character':s.count('Missing character'),'overfull_boxes':s.count('Overfull'),
  'undefined_reference_warning':len(re.findall(r'(?:There were undefined references|Reference .* undefined|Citation .* undefined)',s)),
  'underfull_boxes':s.count('Underfull'),'font_warning_count':s.count('LaTeX Font Warning'),
  'label_rerun_warning':'Label(s) may have changed' in s,
  'other_warnings':re.findall(r'(?:LaTeX Warning:|Package \w+ Warning:)[^\n]*',s),
 }
result={'old_numbered_entries':sum(a.values()),'new_numbered_entries':sum(b.values()),'added_entry_count':len(new_ids),'added_entries':new_ids,
 'old_formula_tag_count':sum(ta.values()),'new_formula_tag_count':sum(tb.values()),'added_formula_tags':list((tb-ta).elements()),
 'new_tikzcd_diagrams':addition.count('\\begin{tikzcd}'), 'body_translator_notes':note_ids,
 'old_body_files_preserved_byte_for_byte':body_ok,'old_body_files_changed':body_changes,'logs':logs}
(ROOT/'checks/structure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
