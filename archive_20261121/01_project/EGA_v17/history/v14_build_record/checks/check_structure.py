from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R))
from flatten_sources import expand
s=expand(R/'main.tex')
entries=re.findall(r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}',s)
tags=re.findall(r'\\tag\{([^}]+)\}',s)
old=json.loads((R/'checks/baseline_v13_counters.json').read_text())
newfiles=[R/'continuations'/f'iv0_22_{n}.tex' for n in ['4a','4b','5a','5b']]
new='\n'.join(p.read_text() for p in newfiles)
res={'old_entry_count':len(old['entries']),'new_entry_count':len(entries),'old_tag_count':len(old['tags']),'new_tag_count':len(tags),'lost_entries':list((Counter(old['entries'])-Counter(entries)).elements()),'lost_tags':list((Counter(old['tags'])-Counter(tags)).elements())}
for key,fn in [('math','baseline_v13_math_sha256.json'),('report','baseline_v13_report_sha256.json')]:
 baseline=json.loads((R/'checks'/fn).read_text())
 res['previous_'+key+'_files']=len(baseline)
 res['changed_previous_'+key+'_files']=[f for f,h in baseline.items() if hashlib.sha256((R/f).read_bytes()).hexdigest()!=h]
res['new_entries']=re.findall(r'\\(?:egapar|egastatement|egap|egas)\{([^}]+)\}',new)
res['new_tags']=re.findall(r'\\tag\{([^}]+)\}',new)
res['new_notes']=re.findall(r'\\cmt\{([^}]+)\}',new)
res['new_tikzcd_blocks']=new.count(r'\begin{tikzcd}')
(R/'checks/structure.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print(json.dumps(res,ensure_ascii=False,indent=2))
if res['lost_entries'] or res['lost_tags'] or res['changed_previous_math_files'] or res['changed_previous_report_files']:sys.exit(1)
