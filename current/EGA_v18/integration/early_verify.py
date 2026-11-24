#!/usr/bin/env python3
"""Literal and structural retention checks; not a proof checker."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
W=Path(__file__).resolve().parents[1]; R=W.parents[1]
J=json.loads((W/'integration/early_migration.json').read_text())
body='\n'.join((W/p).read_text() for p in J['input_order'])
report=(W/J['report']['path']).read_text(); combined=body+'\n'+report
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def arg(s,i):
    assert s[i]=='{'; d=1; j=i+1
    while d:
        if s[j]=='\\' and s[j+1] in '{}%': j+=2; continue
        if s[j]=='{': d+=1
        elif s[j]=='}': d-=1
        j+=1
    return s[i+1:j-1],j
def notes(s):
    out=[]
    for m in re.finditer(r'\\footnote\{',s): out.append(arg(s,m.end()-1)[0])
    return out
pat=re.compile(r'\\\[(.*?)\\\]|\\\((.*?)\\\)|(?<!\\)\$(?!\$)(.*?)(?<!\\)\$|\\begin\{(equation\*?|align\*?|gather\*?|tikzcd)\}(.*?)\\end\{\4\}',re.S)
results=[]; note_total=0
for b in J['batches']:
    s=(R/b['source']).read_text(); p=W/b['output']['path']
    checks={'source_hash':h(R/b['source'])==b['source_sha256'], 'output_hash':h(p)==b['output']['sha256']}
    source_notes=notes(s); absent=[]
    for note in source_notes:
        expected=note
        for edit in J['edits']:
            if edit['batch']==b['batch']: expected=expected.replace(edit['old'],edit['new'])
        if expected not in combined: absent.append({'sha256':hashlib.sha256(note.encode()).hexdigest(),'text':note})
    checks['footnotes_preserved_after_explicit_edits']=not absent
    # Range union prevents double-counting the 2.12 subsection moved to report.
    ranges=[]
    for a,z in sorted((v['start_offset'],v['end_offset']) for v in b['ranges']):
        if ranges and a<=ranges[-1][1]: ranges[-1][1]=max(z,ranges[-1][1])
        else: ranges.append([a,z])
    fragments=[m.group() for a,z in ranges for m in pat.finditer(s[a:z])]
    missing=[t for t in fragments if t not in combined]
    checks['migrated_math_fragments_found_verbatim']=not missing
    anchors=re.findall(r'\\ega[ps]\{([^{}]+)\}',p.read_text())
    results.append({'batch':b['batch'],'checks':checks,'source_footnotes':len(source_notes),'missing_notes':absent,
                    'mathematical_fragments':len(fragments),'missing_math':missing,'anchors':anchors})
    note_total+=len(source_notes)
anchors=re.findall(r'\\ega[ps]\{([^{}]+)\}',body)
duplicates={k:v for k,v in Counter(anchors).items() if v>1}
old={p:{'record_matches':h(W/p)==x,'archive_matches':h(W/p)==h(R/'archive_20261121/01_project/EGA_v17'/p)} for p,x in J['untouched_old_sources'].items()}
old_notes=all(n['text'] in report for n in J['old_annotations'])
status_patterns=[r'未改(?:动)?1158',r'待替换',r'留待下(?:一)?批',r'本批未',r'不属于本批']
stale=[{'pattern':p,'match':m.group()} for p in status_patterns for m in re.finditer(p,body)]
answer={'scope':'Structural/literal retention and original-byte checks only; no full mathematical audit.',
 'passed':all(all(x['checks'].values()) for x in results) and not duplicates and old_notes and not stale and all(all(x.values()) for x in old.values()),
 'batches':results,'raw_batch_footnotes_total':note_total,'old_annotations_retained_verbatim':len(J['old_annotations']) if old_notes else False,
 'body_anchor_count':len(anchors),'duplicate_body_anchors':duplicates,'old_sources':old,'obsolete_body_progress_hits':stale,
 'limitations':['Mathematical-fragment membership is not a semantic equivalence proof.','All raw original batch sources stay immutable in dot_updates_20261124.','Coverage of source pages is limited to the separately recorded actual image inspection.']}
(W/'integration/early_verification.json').write_text(json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':answer['passed'],'raw_footnotes':note_total,'old_notes':len(J['old_annotations']),'body_anchors':len(anchors),'duplicates':duplicates,'stale_hits':stale},ensure_ascii=False))
if not answer['passed']: raise SystemExit(1)
