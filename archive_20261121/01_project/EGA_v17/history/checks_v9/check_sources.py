#!/usr/bin/env python3
"""Check source coverage, inclusion and retained files against the supplied v8."""
from pathlib import Path
import collections, hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
new_files=[ROOT/'continuations'/x for x in ['iv0_20_12.tex','iv0_20_3.tex','iv0_20_4.tex','iv0_20_5.tex']]
text='\n'.join(p.read_text() for p in new_files)
entries=re.findall(r'\\ega(?:p|s)\{([^}]+)\}',text)
expected=[f'20.{s}.{i}' for s,n in [(1,7),(2,5),(3,8),(4,14),(5,15)] for i in range(1,n+1)]
assert entries==expected, (entries,expected)
tags=re.findall(r'\\tag\{([^}]+)\}',text)
assert len(tags)==57 and len(set(tags))==57
notes=re.findall(r'\\cmt\{(I9-[^}]+)\}',text)
assert len(notes)==len(set(notes))
main=(ROOT/'main.tex').read_text()
for p in new_files: assert main.count('\\input{'+str(p.relative_to(ROOT))+'}')==1
old=json.loads((ROOT/'checks/baseline_body_sha256.json').read_text())
# The baseline is a dictionary of project-relative filenames to SHA-256 values.
changed=[]; retained=[]; missing=[]
for name,h in old.items():
 p=ROOT/name
 if not p.is_file():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
 else:retained.append(name)
assert not missing
assert changed==['text/remaining.tex'] or set(changed)=={'text/remaining.tex'}, changed
# Scope/range page text is intentionally updated; mathematical body remains unchanged.
single=(ROOT/'single.tex').read_text()
base=json.loads((ROOT/'checks/baseline_structure_v8.json').read_text())
pat=r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}'
before=collections.Counter(base['entries']);after=collections.Counter(re.findall(pat,single))
assert not (before-after)
oldtags=collections.Counter(base['tags']);newtags=collections.Counter(re.findall(r'\\tag\{([^}]+)\}',single))
assert not (oldtags-newtags)
result={
 'new_entries':len(entries),'entry_ids':entries,'new_formula_tags':len(tags),'formula_tags':tags,
 'new_tikzcd_diagrams':text.count('\\begin{tikzcd}'),'new_footnotes':len(notes),'note_ids':notes,
 'retained_baseline_files':len(retained),'intentionally_updated_scope_files':changed,'missing_files':missing,
 'old_entry_instances':sum(before.values()),'new_total_entry_instances':sum(after.values()),
 'old_formula_tag_instances':sum(oldtags.values()),'new_total_formula_tag_instances':sum(newtags.values()),
 'old_entry_instances_lost':dict(before-after),'old_formula_tag_instances_lost':dict(oldtags-newtags),
 'status':'passed'}
(ROOT/'checks/source_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['entry_ids','formula_tags','note_ids']},ensure_ascii=False,indent=2))
